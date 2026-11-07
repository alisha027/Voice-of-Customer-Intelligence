
from sqlalchemy import text
from app.database.connection import engine


def get_analytics_overview():

    with engine.connect() as connection:

        # 1. Overall KPIs
        overview = connection.execute(
            text("""
                SELECT
                    COUNT(*) AS total_feedback,
                    COUNT(DISTINCT uuid) AS unique_reviews,
                    COUNT(*) FILTER (
                        WHERE sentiment = 'Negative'
                    ) AS negative_feedback,
                    MIN(engagement_date) AS start_date,
                    MAX(engagement_date) AS end_date
                FROM enriched_unified_data
            """)
        ).mappings().one()

        total = overview["total_feedback"]
        negative = overview["negative_feedback"]

        # 2. Sentiment distribution
        sentiment_rows = connection.execute(
            text("""
                SELECT
                    COALESCE(sentiment, 'Unknown') AS sentiment,
                    COUNT(*) AS count
                FROM enriched_unified_data
                GROUP BY sentiment
                ORDER BY count DESC
            """)
        ).mappings().all()

        sentiment_distribution = [
            {
                "sentiment": row["sentiment"],
                "count": row["count"],
                "percentage": round(
                    row["count"] / total * 100, 2
                ) if total else 0
            }
            for row in sentiment_rows
        ]

        # 3. Feedback source distribution
        source_rows = connection.execute(
            text("""
                SELECT
                    COALESCE(data_source_type, 'Unknown') AS source,
                    COUNT(*) AS count
                FROM enriched_unified_data
                GROUP BY data_source_type
                ORDER BY count DESC
            """)
        ).mappings().all()

        source_distribution = [
            {
                "source": row["source"],
                "count": row["count"],
                "percentage": round(
                    row["count"] / total * 100, 2
                ) if total else 0
            }
            for row in source_rows
        ]

    return {
        "total_feedback": total,
        "unique_reviews": overview["unique_reviews"],
        "negative_feedback": negative,
        "negative_sentiment_percentage": round(
            negative / total * 100, 2
        ) if total else 0,
        "analysis_period": {
            "start": (
                overview["start_date"].isoformat()
                if overview["start_date"] else None
            ),
            "end": (
                overview["end_date"].isoformat()
                if overview["end_date"] else None
            )
        },
        "sentiment_distribution": sentiment_distribution,
        "source_distribution": source_distribution
    }
