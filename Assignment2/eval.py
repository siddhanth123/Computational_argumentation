import argparse
import json

from sklearn.metrics import f1_score, precision_score, recall_score


def main():
    with open(args.true, "r") as f:
        true_data = json.load(f)
    with open(args.predictions, "r") as f:
        pred_data = json.load(f)

    # Unpack all sentences into a dict where the id is the key
    # and the value the text of the sentence
    true_ids = []
    true_labels = []
    for sentence in true_data:
        true_ids.append(sentence["id"])
        true_labels.append(sentence["label"])

    y_pred = [int(pred_data[i]) for i in true_ids]

    # Calculate actual score
    print("Precision:", precision_score(true_labels, y_pred))
    print("Recall:", recall_score(true_labels, y_pred))
    print("F1:", f1_score(true_labels, y_pred))


if __name__ == "__main__":
    # Add cli parameters
    parser = argparse.ArgumentParser("Script to evaluate the predictions on a test set.")

    parser.add_argument(
        "--true",
        "-t",
        required=True,
        help="Path to the test data file containing the true labels.",
        metavar="TEST_DATA")
    parser.add_argument(
        "--predictions",
        "-p",
        required=True,
        help="Path to the predictions file in the specified format.",
        metavar="PREDICTIONS")

    args = parser.parse_args()

    main()

    print("Done.")
