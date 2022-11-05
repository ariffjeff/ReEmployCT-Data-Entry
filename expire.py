import os
import time

# def parseCredentials(cred_filename):
#     with open(cred_filename, 'r') as cred_in:
#         lines = cred_in.readlines()
#         creds = {}
#         for line in lines:
#             tuples = line.rstrip('\n').split('=', 1)
#             if(len(tuples) == 2):
#                 creds[tuples[0]] = tuples[1]
#     return creds

# def parseCredentials(cred_filename):
#     with open(cred_filename, 'r') as cred_in:
#         lines = cred_in.readlines()
#         config = {}
#         for line in lines:
#             tuples = line.rstrip('\n').split('=', 1)
#             if tuples[0] in ('Expiry '):
#                 config[tuples[0]] = tuples[1]
#     return config

# def are_creds_expired(expiry_time):
#     if(expiry_time == '-1' or time.time() <= float(expiry_time)): # -1 means credentials never expire
#         return False
#     return True


# def main():
#     key_file = 'key.key'
#     key_exp_start = time.time()
#     cred_filename = 'CredFile.ini'
#     config = parseCredentials(cred_filename)

#     # if not(are_creds_expired(config)):
#     #     time_for_exp = int(config['Expiry']) * 60 # seconds
#     #     while(os.path.isfile(key_file)):
#     #         time.sleep(10)
#     #         if (not(time.time() - key_exp_start <= time_for_exp)
#     #             and os.path.isfile(key_file)):
#     #             os.remove(key_file)

# if __name__ == "__main__":
# 	main()
