import time, os, requests
from kubernetes import client, config

# Environment variables (passed from Kubernetes Deployment)
LABEL_SELECTOR = os.getenv("LABEL_SELECTOR", "app=avva-app")
NAMESPACE = os.getenv("NAMESPACE", "default")
ANNOTATION_KEY = os.getenv("ANNOTATION_KEY", "ava/self-heal-count")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "15"))
LOG_LINES = int(os.getenv("LOG_LINES", "50"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # optional (ServiceNow / Ansible / PowerAutomate webhook)

def get_annotation(pod):
    ann = pod.metadata.annotations or {}
    return int(ann.get(ANNOTATION_KEY, "0"))

def set_annotation(v1, pod, count):
    body = {"metadata": {"annotations": {ANNOTATION_KEY: str(count)}}}
    v1.patch_namespaced_pod(name=pod.metadata.name, namespace=NAMESPACE, body=body)

def trigger_webhook(pod, reason, logs):
    if not WEBHOOK_URL:
        print("WEBHOOK_URL not set — skipping webhook.")
        return
    payload = {
        "pod": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "reason": reason,
        "logs": logs
    }
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print("Webhook status:", r.status_code)
    except Exception as e:
        print("Webhook call failed:", e)

def main():
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    while True:
        try:
            pods = v1.list_namespaced_pod(namespace=NAMESPACE, label_selector=LABEL_SELECTOR).items

            for pod in pods:
                statuses = pod.status.container_statuses or []
                failed = False
                reason = ""

                for cs in statuses:
                    if cs.last_state and cs.last_state.terminated and cs.last_state.terminated.exit_code != 0:
                        failed = True
                        reason = cs.last_state.terminated.reason or "Exit code != 0"
                    if cs.state and cs.state.waiting and cs.state.waiting.reason in ["CrashLoopBackOff", "Error", "ImagePullBackOff"]:
                        failed = True
                        reason = cs.state.waiting.reason

                if not failed:
                    if get_annotation(pod) != 0:
                        set_annotation(v1, pod, 0)
                    continue

                # Fetch logs
                try:
                    logs = v1.read_namespaced_pod_log(name=pod.metadata.name, namespace=NAMESPACE, tail_lines=LOG_LINES)
                except:
                    logs = "Unable to fetch logs."

                # Retry logic
                attempts = get_annotation(pod) + 1
                set_annotation(v1, pod, attempts)

                print(f"Pod {pod.metadata.name} failed ({reason}). Attempt {attempts}/{MAX_RETRIES}")

                if attempts >= MAX_RETRIES:
                    print("Max retries reached — triggering webhook.")
                    trigger_webhook(pod, reason, logs)
                    continue

                # Restart by deleting pod
                try:
                    v1.delete_namespaced_pod(name=pod.metadata.name, namespace=NAMESPACE)
                    print(f"Deleted pod {pod.metadata.name} for restart.")
                except Exception as e:
                    print("Error deleting pod:", e)

            time.sleep(POLL_INTERVAL)

        except Exception as e:
            print("Error in main loop:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
