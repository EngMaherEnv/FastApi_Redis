import csv
import pandas as pd
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_csv(input_file_path, output_file_path, chunk_size=1000):
    song_data = defaultdict(lambda: defaultdict(int))

    logger.info(f"Reading input file: {input_file_path}")
    for chunk in pd.read_csv(input_file_path, chunksize=chunk_size):
        for index, row in chunk.iterrows():
            song = row['Song']
            date = row['Date']
            plays = int(row['Number of Plays'])
            song_data[song][date] += plays

    logger.info(f"Finished reading input file: {input_file_path}")

    aggregated_data = []
    for song in sorted(song_data):
        for date in sorted(song_data[song]):
            total_plays = song_data[song][date]
            aggregated_data.append([song, date, total_plays])

    logger.info(f"Writing to output file: {output_file_path}")
    with open(output_file_path, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Song', 'Date', 'Total Number of Plays for Date'])
        writer.writerows(aggregated_data)

    logger.info(f"Finished writing to output file: {output_file_path}")
