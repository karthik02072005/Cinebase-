
from flask import Flask, jsonify, request, send_from_directory
from db.connection import get_connection
from flask_cors import CORS
from werkzeug.exceptions import NotFound

app = Flask(__name__, static_folder='public', static_url_path='/')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/movies', methods=['GET'])
def get_movies():
    search_term = request.args.get('q', '')
    
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        m.Movie_ID AS id, m.Title_English AS title, m.Release_Year AS year, m.Duration_Min AS duration, 
        m.IMDB_Rating AS rating, m.Plot_Summary AS plot, i.Industry_Name AS industry,
        bo.Budget_INR_Cr AS budget, bo.Revenue_INR_Cr AS revenue,
        
        GROUP_CONCAT(DISTINCT g.Genre_Name) AS genres,
        (SELECT GROUP_CONCAT(CONCAT(P.Name, ' (', MPR.Role_Description, ')') SEPARATOR '; ')
         FROM Movie_Person_Role MPR JOIN Person P ON MPR.Person_ID = P.Person_ID 
         WHERE MPR.Movie_ID = m.Movie_ID) AS cast_crew,
        (SELECT GROUP_CONCAT(A.Award_Name) FROM Award A WHERE A.Movie_ID = m.Movie_ID) AS awards
         
    FROM Movies m
    JOIN Industry i ON m.Industry_ID = i.Industry_ID
    LEFT JOIN Box_Office bo ON m.Movie_ID = bo.Movie_ID
    LEFT JOIN Movie_Genre mg ON m.Movie_ID = mg.Movie_ID
    LEFT JOIN Genre g ON mg.Genre_ID = g.Genre_ID
    
    WHERE m.Title_English LIKE %s OR m.Plot_Summary LIKE %s
    
    GROUP BY m.Movie_ID
    ORDER BY m.Release_Year DESC;
    """
    
    search_param = f"%{search_term}%"

    try:
        cursor.execute(query, (search_param, search_param))
        rows = cursor.fetchall()
        return jsonify(rows)
    except Exception as e:
        print(f"FATAL SQL EXECUTION ERROR in GET_MOVIES: {e}") 
        return jsonify({'error': 'Internal Server Error during data retrieval.'}), 500 
    finally:
        cursor.close()
        conn.close()

@app.route('/api/filmography_search', methods=['GET'])
def filmography_search():
    person_names_str = request.args.get('names', '')
    start_year_str = request.args.get('start_year')
    end_year_str = request.args.get('end_year')
    
    try:
        start_year = int(start_year_str)
        end_year = int(end_year_str)
    except (ValueError, TypeError):
        return jsonify({'error': 'Start Year and End Year must be valid integers.'}), 400
    
    person_names = [name.strip() for name in person_names_str.split(',') if name.strip()]
    
    if not person_names:
        return jsonify({'error': 'At least one name is required.'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    name_placeholders = ', '.join(['%s'] * len(person_names))
    
    query = f"""
        SELECT
            M.Movie_ID,
            M.Title_English AS title,
            M.Release_Year AS year,
            GROUP_CONCAT(DISTINCT I.Industry_Name) AS industries
        FROM Movies M
        JOIN Movie_Person_Role MPR ON M.Movie_ID = MPR.Movie_ID
        JOIN Person P ON MPR.Person_ID = P.Person_ID
        JOIN Industry I ON M.Industry_ID = I.Industry_ID
        WHERE 
            P.Name IN ({name_placeholders}) 
            AND M.Release_Year BETWEEN %s AND %s
        GROUP BY M.Movie_ID
        HAVING COUNT(DISTINCT P.Name) = %s
        ORDER BY M.Release_Year DESC;
    """

    params = person_names + [start_year, end_year, len(person_names)]
    
    try:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        return jsonify({
            'count': len(rows),
            'movies': rows
        })
        
    except Exception as e:
        print(f"SQL Collaboration Search Error: {e}")
        return jsonify({'error': f'Database execution failed: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/movies', methods=['POST'])
def create_movie():
    data = request.json or {}
    
    title = data.get('title')
    year = data.get('year')
    duration = data.get('duration')
    rating = data.get('rating')
    plot = data.get('plot')
    industry_id = data.get('industry')
    budget = data.get('budget')
    revenue = data.get('revenue')
    
    genres_str = data.get('genres', '')
    cast_str = data.get('cast', '')
    awards_str = data.get('awards', '')

    if not all([title, year, industry_id]):
        return jsonify({'error': 'Title, Year, and Industry ID required'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("START TRANSACTION;")

        movie_query = """INSERT INTO Movies (Title_English, Release_Year, Duration_Min, Plot_Summary, IMDB_Rating, Industry_ID)
                         VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(movie_query, (title, year, duration, plot, rating, industry_id))
        new_id = cursor.lastrowid
  
        if budget is not None or revenue is not None:
 
            bo_fields = []
            bo_values = []
            if budget is not None:
                bo_fields.append("Budget_INR_Cr = %s")
                bo_values.append(budget)
            if revenue is not None:
                bo_fields.append("Revenue_INR_Cr = %s")
                bo_values.append(revenue)
                
            box_office_update_query = "UPDATE Box_Office SET " + ", ".join(bo_fields) + " WHERE Movie_ID = %s"
            cursor.execute(box_office_update_query, bo_values + [new_id])

        for genre_name in genres_str.split(','):
            genre_name = genre_name.strip()
            if not genre_name: continue
            
            cursor.execute("INSERT IGNORE INTO Genre (Genre_Name) VALUES (%s)", (genre_name,))
            cursor.execute("SELECT Genre_ID FROM Genre WHERE Genre_Name = %s", (genre_name,))
            genre_id = cursor.fetchone()['Genre_ID']
            cursor.execute("INSERT INTO Movie_Genre (Movie_ID, Genre_ID) VALUES (%s, %s)", (new_id, genre_id))

        for entry in cast_str.split(','):
            parts = entry.split(':')
            if len(parts) != 2: continue
            person_name = parts[0].strip()
            role_desc = parts[1].strip()
            
            cursor.execute("INSERT IGNORE INTO Person (Name, Role_Type) VALUES (%s, %s)", (person_name, role_desc))
            cursor.execute("SELECT Person_ID FROM Person WHERE Name = %s", (person_name,))
            person_id = cursor.fetchone()['Person_ID']

            cursor.execute("INSERT INTO Movie_Person_Role (Movie_ID, Person_ID, Role_Description) VALUES (%s, %s, %s)", 
                           (new_id, person_id, role_desc))

        for award_name in awards_str.split(','):
            award_name = award_name.strip()
            if not award_name: continue
            cursor.execute("INSERT INTO Award (Movie_ID, Award_Name, Award_Year) VALUES (%s, %s, %s)", 
                           (new_id, award_name, year))

        conn.commit()
        return jsonify({'success': True, 'Movie_ID': new_id}), 201

    except Exception as e:
        conn.rollback()
        print(f"FATAL INSERT TRANSACTION ERROR: {e}") 
        return jsonify({'success': False, 'error': str(e)}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    data = request.json or {}
    
    movie_fields = {}
    box_office_fields = {}
    
    db_mapping = {
        'title': 'Title_English', 'year': 'Release_Year', 'duration': 'Duration_Min', 
        'rating': 'IMDB_Rating', 'plot': 'Plot_Summary', 'industry': 'Industry_ID',
        'budget': 'Budget_INR_Cr', 'revenue': 'Revenue_INR_Cr'
    }

    for frontend_key, db_column in db_mapping.items():
        if frontend_key in data:
            if db_column in ['Budget_INR_Cr', 'Revenue_INR_Cr']:
                box_office_fields[db_column] = data[frontend_key]
            else:
                movie_fields[db_column] = data[frontend_key]
            
    if not movie_fields and not box_office_fields:
        return jsonify({'error': 'No updatable fields provided'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("START TRANSACTION;")

        if movie_fields:
            movie_set_clause = ", ".join([f"{k} = %s" for k in movie_fields.keys()])
            movie_values = list(movie_fields.values())
            
            movie_set_clause = movie_set_clause.replace('title', 'Title_English').replace('year', 'Release_Year').replace('duration', 'Duration_Min')
            movie_set_clause = movie_set_clause.replace('rating', 'IMDB_Rating').replace('plot', 'Plot_Summary').replace('industry', 'Industry_ID')
            
            query_movies = f"UPDATE Movies SET {movie_set_clause} WHERE Movie_ID = %s"
            cursor.execute(query_movies, tuple(movie_values + [movie_id]))

        if box_office_fields:
            bo_set_clause = ", ".join([f"{k} = %s" for k in box_office_fields.keys()])
            bo_values = list(box_office_fields.values())
            
            bo_set_clause = bo_set_clause.replace('budget', 'Budget_INR_Cr').replace('revenue', 'Revenue_INR_Cr')
            
            query_update_bo = f"UPDATE Box_Office SET {bo_set_clause} WHERE Movie_ID = %s"
            cursor.execute(query_update_bo, tuple(bo_values + [movie_id]))


        conn.commit()
        return jsonify({'success': True}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
        
    finally:
        cursor.close()
        conn.close()

@app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "DELETE FROM Movies WHERE Movie_ID = %s"
        affected_rows = cursor.execute(query, (movie_id,))
        if affected_rows == 0:
            raise NotFound(f"Movie with ID {movie_id} not found.")
            
        conn.commit()
        return jsonify({'success': True})
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(port=3000, debug=True)