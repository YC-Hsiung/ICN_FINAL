# the last argument can be 'webcam' or 'file'
source ./config
python run_client.py $file_path $client_host $server_port $client_rtp_port $src_type
