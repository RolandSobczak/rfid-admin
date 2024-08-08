cd /home/rsobczak/code/RFIDIO-Backend

git_sha=$(git rev-parse HEAD)

if [ -z "$git_sha" ]; then
    echo "Error: Git SHA is empty. Please check if you're in a valid Git repository."
    exit 1
fi

rfid_auth="localhost:32000/rfidio-auth-auth:${git_sha}"
rfid_auth_latest="localhost:32000/rfidio-auth:latest"

docker build -t $rfid_auth  -t $rfid_auth_latest -f docker/auth/auth.dockerfile .
docker push $rfid_auth
docker push $rfid_auth_latest

rfid_tenant="localhost:32000/rfidio-tenant:${git_sha}"
rfid_tenant_latest="localhost:32000/rfidio-tenant:latest"

docker build -t $rfid_tenant -t $rfid_tenant_latest -f docker/tenant/tenant.dockerfile .
docker push $rfid_tenant
docker push $rfid_tenant_latest

rfid_external="localhost:32000/rfidio-external:${git_sha}"
rfid_external_latest="localhost:32000/rfidio-external:latest"

docker build -t $rfid_external -t $rfid_external_latest -f docker/external/external.dockerfile .
docker push $rfid_external
docker push $rfid_external_latest

cd -
