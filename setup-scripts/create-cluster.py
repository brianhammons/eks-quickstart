from __future__ import print_function
from botocore.vendored import requests
import cfnresponse
import sys, os, base64, datetime, hashlib, hmac, json

def lambda_handler(event, context):
    response = {
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Status': 'SUCCESS'
    }

    request_parameters = {
        "clusterName": str(event['ResourceProperties']['ClusterName']),
        "roleArn": str(event['ResourceProperties']['RoleArn']),
        "vpcId": str(event['ResourceProperties']['VPC']),
        "subnets": str(event['ResourceProperties']['SubnetIds']).split(" "),
        "securityGroups": [str(event['ResourceProperties']['SecurityGroups'])]
    }

    if event['RequestType'] == 'Create':
      method = 'POST'
      path = '/clusters'

    if event['RequestType'] == 'Delete':
      method = 'DELETE'
      path = '/clusters/' + request_parameters['clusterName']

    request_parameters = json.dumps(request_parameters)
    host = 'eks.us-west-2.amazonaws.com'
    region = event['ResourceProperties']['Region']
    service = 'eks'
    endpoint = 'https://eks.us-west-2.amazonaws.com'
    request_url = endpoint + path
    content_type = 'application/json'

    def sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def getSignatureKey(key, date_stamp, regionName, serviceName):
        kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
        kRegion = sign(kDate, regionName)
        kService = sign(kRegion, serviceName)
        kSigning = sign(kService, 'aws4_request')
        return kSigning
    
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')

    canonical_uri = path
    canonical_querystring = ''               
    canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-amz-date:' + amz_date + '\n'
    signed_headers = 'content-type;host;x-amz-date'          
    
    access_key = os.environ.get('AWS_ACCESS_KEY')
    secret_key = os.environ.get('AWS_SECRET_KEY')
    if access_key is None or secret_key is None:
      print('No access key is available.')
      sys.exit()

    payload_hash = hashlib.sha256(request_parameters).hexdigest()
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request).hexdigest()
    signing_key = getSignatureKey(secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
    
    headers = {'Content-Type':content_type,
           'Host':host,
           'X-Amz-Date':amz_date,
           'Authorization':authorization_header}
    try:
      if event['RequestType'] == 'Create':
        r = requests.post(request_url, data=request_parameters, headers=headers)
      if event['RequestType'] == 'Delete':
        r = requests.delete(request_url, data=request_parameters, headers=headers)
      responseData = json.loads(r.text)
      print('Response code: %d' % r.status_code)
      return cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, "CustomResourcePhysicalID")
    except Exception as E:
      response['Reason'] = 'Event Failed - See CloudWatch logs for the Lamba function backing the custom resource for details'
      return cfnresponse.send(event, context, cfnresponse.FAILED, responseData, "CustomResourcePhysicalID")