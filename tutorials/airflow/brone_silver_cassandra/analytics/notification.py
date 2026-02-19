# By adding connectors in Microsoft Teams,
# you can post notification to the connection
import requests


def post_notification(message, teams_webhook):
    context = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": message,
        "sections": [
            {
                "activityTitle": message,
                "activitySubtitle": "Airflow",
            }
        ],
    }
    x = requests.post(teams_webhook, json=context)
    print(x.text)


# def post_notification(gcs_report, teams_webhook):
#     context = {
#         "@type": "MessageCard",
#         "@context": "http://schema.org/extensions",
#         "themeColor": "0076D7",
#         "summary": f"Analytic report {gcs_report} ready",
#         "sections": [
#             {
#                 "activityTitle": f"Analytic report {gcs_report} is ready for review",
#                 "activitySubtitle": "Airflow",
#             }
#         ],
#     }
#     x = requests.post(teams_webhook, json=context)
#     print(x.text)
