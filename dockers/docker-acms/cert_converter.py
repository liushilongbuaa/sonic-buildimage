#!/usr/bin/env python

'''
This script converts every downloaded cert from dSMS in .pfx format to .crt and .key format.
It watches for changes to the uber notify file by dSMS and triggers the conversion process
'''

import os, subprocess, time
import random, string
from sonic_py_common import logger

# Location where this script finally puts the certs after format conversion
certs_path = "/etc/sonic/credentials/"
# Location where ACMS downloads certs from dSMS
acms_certs_path = "/var/opt/msft/client/dsms/sonic-prod/certificates/chained/"
# Location of the uber notify file
uber_notify_file_path = "/var/opt/msft/client/anysecret.notify"
# Length of password for private key encryption
password_length = 64
# Duration between polling for cert changes in seconds
polling_frequency = 3600

sonic_logger = logger.Logger()
sonic_logger.set_min_log_priority_info()

def execute_cmd(cmd):
    response = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = response.communicate()
    if (response.returncode != 0):
        sonic_logger.log_error(stderr, True)
        return False
    return True

def get_list_of_certs(path):
    # Make list of the certs at a given location
    files = [file_t for file_t in os.listdir(path) if (os.path.isfile(os.path.join(path, file_t)) and not os.path.islink(os.path.join(path, file_t)))]
    cert_list = []
    supported_cert_ext = ['pfx', 'crt', 'key']
    for file_t in files:
        if ("notify" not in file_t) and ("metadata" not in file_t):
            file_ext = file_t.split(".")[1]
            file_name = file_t.split(".")[0]
            if (file_ext in supported_cert_ext) and ("sonic_acms_bootstrap" not in file_name) and ("temp" not in file_name) and ("test" not in file_name):
                cert_name = file_name
                cert_ver = file_t.split(".")[2]
                cert_list.append(cert_name+"."+cert_ver)
    cert_list = list(set(cert_list))
    return cert_list

def link_to_latest_cert(acms_certs_path, certs_path):
    # Create symlink to latest cert file
    link_files = [f for f in os.listdir(certs_path) if (os.path.isfile(os.path.join(certs_path, f)) and os.path.islink(os.path.join(certs_path, f)))]
    targets = []
    for link in link_files:
        targets.append(os.readlink(os.path.join(certs_path, link)))
    notify_files = [f for f in os.listdir(acms_certs_path) if (os.path.isfile(os.path.join(acms_certs_path, f)) and (".notify" in f))]
    for n_file in notify_files:
        cert_name = n_file.split(".")[0]
        sonic_logger.log_info("cert_converter : link_to_latest_cert : Linking cert "+cert_name+".pfx")
        cert_ver = open(acms_certs_path+n_file, "r").readline().split(acms_certs_path)[1].split(".")[2]
        if certs_path+cert_name+".crt."+cert_ver not in targets:
            cmd = "ln -s -f "+certs_path+cert_name+".crt."+cert_ver+" "+certs_path+cert_name+".crt"
            sonic_logger.log_notice("cert_converter : link_to_latest_cert : "+cmd, True)
            if not execute_cmd(cmd):
                return False
        if certs_path+cert_name+".key."+cert_ver not in targets:
            cmd = "ln -s -f "+certs_path+cert_name+".key."+cert_ver+" "+certs_path+cert_name+".key"
            sonic_logger.log_notice("cert_converter : link_to_latest_cert : "+cmd, True)
            if not execute_cmd(cmd):
                return False
        sonic_logger.log_info("cert_converter : link_to_latest_cert : Finished linking cert "+cert_name+".pfx")
    return True

def convert_certs(acms_certs_path, certs_path, password_length):
    existing_cert_names = get_list_of_certs(certs_path)
    downloaded_cert_names = get_list_of_certs(acms_certs_path)
    new_cert_flag = False

    if len(downloaded_cert_names):
        for cert_name in downloaded_cert_names:
            # Start converting those certs which have not been converted
            if cert_name not in existing_cert_names:
                sonic_logger.log_info("cert_converter : convert_certs : Start converting "+cert_name)
                name = cert_name.split(".")[0]
                ver = cert_name.split(".")[1]
                # Extract the certificate from the pfx file
                cmd = "openssl pkcs12 -clcerts -nokeys -in "+acms_certs_path+name+".pfx."+ver+" -out "+certs_path+name+".crt."+ver+" -password pass: -passin pass:"
                sonic_logger.log_info("cert_converter : convert_certs : "+cmd)
                if not execute_cmd(cmd):
                    sonic_logger.log_error("cert_converter : convert_certs : Extracting crt from pfx failed!", True)
                    return False                
                # Generate a random password for encrypting the private key
                string_choice = string.ascii_uppercase + string.ascii_lowercase + string.digits
                random_password = ''.join(random.choice(string_choice) for _ in range(password_length))
                # Extract the private key from the pfx file
                cmd = "openssl pkcs12 -nocerts -in "+acms_certs_path+name+".pfx."+ver+" -out "+certs_path+"private.key -password pass: -passin pass: -passout pass:"+random_password
                if not execute_cmd(cmd):
                    sonic_logger.log_error("cert_converter : convert_certs : Creating private key from pfx failed!", True)
                    return False
                # Decrypt the private key
                cmd = "openssl rsa -in "+certs_path+"private.key -out "+certs_path+name+".key."+ver+" -passin pass:"+random_password
                if not execute_cmd(cmd):
                    sonic_logger.log_error("cert_converter : convert_certs : Extracting key from pfx failed!", True)
                    return False
                cmd = "rm "+certs_path+"private.key"
                if not execute_cmd(cmd):
                    sonic_logger.log_error("cert_converter : convert_certs : Removing private key failed!", True)
                    return False
                new_cert_flag = True
                sonic_logger.log_info("cert_converter : convert_certs : Finished converting "+cert_name)
            else:
                sonic_logger.log_info("cert_converter : convert_certs : "+cert_name+" already converted")
        if new_cert_flag:
            if not (link_to_latest_cert(acms_certs_path, certs_path)):
                sonic_logger.log_error("cert_converter : convert_certs : linking certs failed!", True)
                return False
    else:
        sonic_logger.log_info("cert_converter : convert_certs : no certs downloaded")
    return True


def main():
    while True:
        sonic_logger.log_info("cert_converter : main : Check if uber_notify_file is present")
        if os.path.isfile(uber_notify_file_path):
            sonic_logger.log_info("cert_converter : main : uber_notify_file found, converting all certs...")
            if not convert_certs(acms_certs_path, certs_path, password_length):
                sonic_logger.log_error("cert_converter : main : Cert conversion failed!")
            break
        else:
            time.sleep(60)

    sonic_logger.log_info("cert_converter : main : Start polling every 1hr...")
    while True:
        sonic_logger.log_notice("cert_converter : main : Checking for cert changes...")
        if not convert_certs(acms_certs_path, certs_path, password_length):
            sonic_logger.log_error("cert_converter : main : Cert conversion failed!")
        time.sleep(polling_frequency)

if __name__ == "__main__":
    main()
