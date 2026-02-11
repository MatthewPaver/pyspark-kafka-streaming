"""Basic PySpark DataFrame creation and display.

Demonstrates creating a SparkSession, building a DataFrame from
in-memory data, and displaying the results.
"""

from pyspark.sql import SparkSession


def main() -> None:
    spark = SparkSession.builder.appName("BasicDataFrame").getOrCreate()

    data = [("James", "Smith"), ("Anna", "Rose"), ("Robert", "Williams")]
    columns = ["FirstName", "LastName"]

    df = spark.createDataFrame(data, columns)
    df.show()

    spark.stop()


if __name__ == "__main__":
    main()
