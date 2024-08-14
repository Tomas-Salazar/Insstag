import instaloader
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

def Datos_post(profile):
    # Crear listas para almacenar la información de cada post
    post_ids = []
    post_likes = []
    post_comments = []
    post_dates = []

    # Obtener información detallada de cada post y almacenarla en las listas
    for post in profile.get_posts():
        post_ids.append(post.shortcode)
        post_likes.append(post.likes)
        post_comments.append(post.comments)
        post_dates.append(post.date_local.replace(tzinfo=None))

    # Crear un DataFrame de Pandas con la información recopilada
    data = {
        'Post_ID': post_ids,
        'Likes': post_likes,
        'Comentarios':post_comments,
        'Fecha_de_creación': post_dates,
    }
    return pd.DataFrame(data)


def main():
    load_dotenv()
    
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    
    connection_string = f'mysql+pymysql://{username}:{password}@{server}/{database}'
    
    engine = create_engine(connection_string)
    
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, 'ssala_')
    
    df = Datos_post(profile)
    
    with engine.begin() as connection:
        delete_sql = text("""
            DELETE FROM instagram_post
            """)
        connection.execute(delete_sql)
        
    df.to_sql('instagram_post', engine, if_exists='append', index=False)
    
    data = {'Fecha': [datetime.today().strftime('%Y-%m-%d')],
            'Seguidores': [profile.followers],
            'Seguidos': [profile.followees]}
    
    df = pd.DataFrame(data)
    with engine.begin() as connection:
        delete_sql = text("""
            DELETE FROM instagram_perfil
            WHERE Fecha >= :fecha
            """)
        connection.execute(delete_sql, {
                'fecha': datetime.today().strftime('%Y-%m-%d'),
            })
        
    df.to_sql('instagram_perfil', engine, if_exists='append', index=False)


if __name__ == '__main__':
    main()