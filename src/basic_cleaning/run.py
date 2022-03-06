#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    logger.info(f"Downloading artifact {args.input_artifact}")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Loading the Dataset")
    dataframe = pd.read_csv(artifact_local_path)

    # remove outliers
    logger.info("removing outliers")
    idx = dataframe['price'].between(
        args.min_price, args.max_price
    )
    dataframe = dataframe[idx].copy()

    # Convert last_review to datetime
    logger.info("converting last_review to datetime")
    dataframe['last_review'] = pd.to_datetime(dataframe['last_review'])

    # Remove observations outside of NYC
    idx = dataframe['longitude'].between(-74.25, -73.50) & dataframe['latitude'].between(40.5, 41.2)
    dataframe = dataframe[idx].copy()

    logger.info(f'Saving Dataframe {args.output_artifact}')
    dataframe.to_csv('clean_sample.csv', index=False)

    # Upload to w&b
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )

    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

    os.remove(args.output_artifact)
    run.finish()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Name for the input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name for the outpt artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description for the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price",
        required=True
    )


    args = parser.parse_args()

    go(args)
