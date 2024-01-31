#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()
    logger.info("Getting the file and loading into dataframe")
    local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(local_path)

    logger.info("getting records between min and max price range")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("converting date from string to datetime")

    df['last_review'] = pd.to_datetime(df['last_review'])

    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    logger.info("saving the cleaned file")
    df.to_csv("clean_sample.csv", index=False)

    logger.info("Logging the artifact to the W&B")
    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)
    run.finish()



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Provide complete path of the input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Provide name of the output artifact to create on W&B",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Provide type of the output artifact to create on W&B",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Provide description about output artifact to save on the W&B",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price of the airbnb to be included in the datdaset",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price of the airbnb to be included in the datdaset",
        required=True
    )


    args = parser.parse_args()

    go(args)
