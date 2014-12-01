import boto

s3 = boto.connect_s3()
print s3
print boto.__dict__