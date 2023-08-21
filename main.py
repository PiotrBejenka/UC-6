import json
import boto3
import datetime

def lambda_handler(event, context):
    
    ec2_client = boto3.client('ec2')
    s3_client = boto3.client('s3')
    
    volumes = ec2_client.describe_volumes()    
    snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])

    encrypted_volumes = {'Attached': {'Number': 0, 'Overall_size': 0}, 'Unattached': {'Number': 0, 'Overall_size': 0}}
    nonencrypted_volumes = {'Attached': {'Number': 0, 'Overall_size': 0}, 'Unattached': {'Number': 0, 'Overall_size': 0}}
    encrypted_snapshots = {'Number': 0, 'Overall_size': 0}
    nonencrypted_snapshots = {'Number': 0, 'Overall_size': 0}
    
    for v in volumes['Volumes']:
        attachment = 'Unattached' if not v.get('Attachments') else 'Attached'
        if v['Encrypted']:
            encrypted_volumes[attachment]['Number'] += 1
            encrypted_volumes[attachment]['Overall_size'] += v['Size']
        else:
            nonencrypted_volumes[attachment]['Number'] += 1
            nonencrypted_volumes[attachment]['Overall_size'] += v['Size']
    
    for s in snapshots['Snapshots']:
        if s.get('Encrypted'):
            encrypted_snapshots['Number'] += 1
            encrypted_snapshots['Overall_size'] += s['VolumeSize']
        else:
            nonencrypted_snapshots['Number'] += 1
            nonencrypted_snapshots['Overall_size'] += s['VolumeSize']

        
    json_data = {
        'Volumes': {
            'Encrypted': encrypted_volumes,
            'Non-Encrypted': nonencrypted_volumes 
        },
        'Snapshots': {
            'Encrypted': encrypted_snapshots,
            'Non-Encrypted': nonencrypted_snapshots
        }
    }

    json_string = json.dumps(json_data)
    
    curr_date = datetime.datetime.now().date()
    file_name = f'volumes_and_snapshots_metrics_{curr_date}.json'
        
    bucket_name='pbeje-uc6-bucket-for-metrics-storage'

    s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=json_string)

    return {
        'statusCode': 200,
        'body': json.dumps('Metrics file uploaded successfully')
    }