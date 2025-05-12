import json

def handle(event, context):
    print(event)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "ok": True
        })
    }