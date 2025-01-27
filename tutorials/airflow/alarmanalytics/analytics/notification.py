# By adding connectors in Microsoft Teams,
# you can post notification to the connection
import requests


def post_notification(gcs_report, teams_webhook):
    context = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "Analytic report {} ready".format(gcs_report),
        "sections": [
            {
                "activityTitle": "Analytic report {} is ready for review".format(
                    gcs_report
                ),
                "activitySubtitle": "Airflow",
            }
        ],
    }
    x = requests.post(teams_webhook, json=context)
    print(x.text)
