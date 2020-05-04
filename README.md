# DBB_2pc
  - Its is a broadcaster that follows two phase commit protocol
  - SocketClient.py is used to push data to be broadcasted
  - Participant.py is used to receive the message via two phase commit and store it in the database
 
 ### API Url
 
    Recovery URL : http:ip:port/recovery
    method: Post
    Request Json: {"PayLoadToken" : 0 } (its the token of the latest data in the DB)
    Response: List of data
    
    Status URL : http:ip:port/status
    method: GET
    Response: {"bufferSize" : size} (size is the queque size)
 
 ### Component Design
 - The atomicity is maintained by performing a two phase commit  
 - The socket server receives the data from the primary node and queues it, performs transactions by dequeuing 
 - This service is also exposed as rest api, for recovering the data and to get the queue status 
 - While it performs the recovery request from any node it halts the two way commit transaction
 
### Procerdure To Run
- Needed Python 3.6
- Needed c++ : Windows => c++ version 2015 | linux => install gcc-c++
- Run command to install requirements : Windows => pip install -r Requirements.txt | linux => pip3 install -r Requirements.txt
