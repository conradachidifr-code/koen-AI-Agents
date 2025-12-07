#!/bin/bash

# Helper script to get MySQL connection details from Minikube

echo "=== Minikube MySQL Connection Helper ==="
echo ""

# Check if minikube is running
if ! minikube status | grep -q "Running"; then
    echo "Error: Minikube is not running. Please start it with 'minikube start'"
    exit 1
fi

echo "Getting MySQL service information..."
echo ""

# Get MySQL service details
kubectl get svc -A | grep mysql

echo ""
echo "To get the MySQL port for port-forwarding, run:"
echo "kubectl get svc -n <namespace> <mysql-service-name> -o jsonpath='{.spec.ports[0].port}'"
echo ""

echo "To set up port forwarding (required to connect from local machine):"
echo "kubectl port-forward -n <namespace> svc/<mysql-service-name> 3306:3306"
echo ""

echo "Alternatively, to use NodePort:"
echo "minikube service -n <namespace> <mysql-service-name> --url"
echo ""

echo "=== Common kubectl commands for MySQL ==="
echo ""
echo "# Get MySQL pods:"
echo "kubectl get pods -A | grep mysql"
echo ""
echo "# Get MySQL password from secret:"
echo "kubectl get secret -n <namespace> <mysql-secret-name> -o jsonpath='{.data.mysql-root-password}' | base64 -d"
echo ""
echo "# Access MySQL shell directly in the pod:"
echo "kubectl exec -it -n <namespace> <mysql-pod-name> -- mysql -u root -p"
