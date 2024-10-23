Created bucket and table manually:

```
aws s3api create-bucket --bucket osm-terraform-storage --region us-east-1
aws s3api list-buckets
aws s3api list-buckets --region us-east-1
aws s3api put-bucket-versioning --bucket osm-terraform-storage --versioning-configuration Status=Enabled
aws s3 cp state-storage.tf s3://osm-terraform-storage/test.tf
aws s3 rm s3://osm-terraform-storage --recursive
# Failed: aws dynamodb create-table     --table-name terraform-locks     --attribute-definitions AttributeName=LockID,AttributeType=S     --key-schema AttributeName=LockID,KeyType=HASH     --billing-mode PAY_PER_REQUEST     --region us-east-1
# Created dynamodb-policy.json
aws iam create-policy --policy-name DynamoDBFullAccess --policy-document file://dynamodb-policy.json
aws iam attach-user-policy --policy-arn arn:aws:iam::507624629289:policy/DynamoDBFullAccess --user-name osm
aws iam list-attached-user-policies --user-name osm
aws dynamodb create-table     --table-name terraform-locks     --attribute-definitions AttributeName=LockID,AttributeType=S     --key-schema AttributeName=LockID,KeyType=HASH     --billing-mode PAY_PER_REQUEST     --region us-east-1
```
