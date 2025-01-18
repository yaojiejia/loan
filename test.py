import requests
import pandas as pd

def dataAnnoation(url):

    tables = pd.read_html(url)

    df = tables[0]
    df.columns = df.iloc[0]
    df = df[1:] 
    
    df['x-coordinate'] = df['x-coordinate'].astype(int)
    df['y-coordinate'] = df['y-coordinate'].astype(int)
    
    df['Character'] = df['Character'].apply(lambda x: x.encode('latin1').decode('utf-8'))

    max_x = df['x-coordinate'].max()
    max_y = df['y-coordinate'].max()

    grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    for _, row in df.iterrows():
        x = int(row['x-coordinate'])
        y = max_y - int(row['y-coordinate'])
        grid[y][x] = row['Character']

    for row in grid:
        print(''.join(row))

dataAnnoation("https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub")
