import requests

webhook_url = "https://discord.com/api/webhooks/1334369568818462774/CtBoUn1u-rjRhO1B0BEp3NZAoRwkyXMYB-j9UwaQgFWY7t4HLrTvE90UdF3yj7aEvHPL"

def send_failure_to_discord(context):
    task_instance = context.get('task_instance')
    dag_name = context.get('dag').dag_id
    task_name = task_instance.task_id
    exception = context.get('exception')

    message = {
        "content": f"**DAG Failed**\nDAG: {dag_name}\ntask: {task_name}\nException: {exception}\n"
    }

    requests.post(webhook_url, json=message)

    