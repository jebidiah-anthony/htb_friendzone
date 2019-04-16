# HTB FriendZone (10.10.10.123) Write-up
## PART 1 : Initial Recon

```console
nmap --min-rate 1000 -p- -v 10.10.10.123
```
```
PORT    STATE SERVICE
21/tcp  open  ftp
22/tcp  open  ssh
53/tcp  open  domain
80/tcp  open  http
139/tcp open  netbios-ssn
443/tcp open  https
445/tcp open  microsoft-ds
```
```console
nmap -oN friendzone -p21,22,53,80,139,445 -sC -sV -v 10.10.10.123
```
```
PORT    STATE SERVICE     VERSION
21/tcp  open  ftp         vsftpd 3.0.3
22/tcp  open  ssh         OpenSSH 7.6p1 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 a9:68:24:bc:97:1f:1e:54:a5:80:45:e7:4c:d9:aa:a0 (RSA)
|   256 e5:44:01:46:ee:7a:bb:7c:e9:1a:cb:14:99:9e:2b:8e (ECDSA)
|_  256 00:4e:1a:4f:33:e8:a0:de:86:a6:e4:2a:5f:84:61:2b (ED25519)
53/tcp  open  domain      ISC BIND 9.11.3-1ubuntu1.2 (Ubuntu Linux)
| dns-nsid:
|_  bind.version: 9.11.3-1ubuntu1.2-Ubuntu
80/tcp  open  http        Apache httpd 2.4.29 ((Ubuntu))
| http-methods:
|_  Supported Methods: HEAD GET POST OPTIONS
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Friend Zone Escape software
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 4.7.6-Ubuntu (workgroup: WORKGROUP)
Service Info: Host: FRIENDZONE; OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_clock-skew: mean: -59m59s, deviation: 1h43m54s, median: 0s
| nbstat: NetBIOS name: FRIENDZONE, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
| Names:
|   FRIENDZONE<00>       Flags: <unique><active>
|   FRIENDZONE<03>       Flags: <unique><active>
|   FRIENDZONE<20>       Flags: <unique><active>
|   \x01\x02__MSBROWSE__\x02<01>  Flags: <group><active>
|   WORKGROUP<00>        Flags: <group><active>
|   WORKGROUP<1d>        Flags: <unique><active>
|_  WORKGROUP<1e>        Flags: <group><active>
| smb-os-discovery:
|   OS: Windows 6.1 (Samba 4.7.6-Ubuntu)
|   Computer name: friendzone
|   NetBIOS computer name: FRIENDZONE\x00
|   Domain name: \x00
|   FQDN: friendzone
|_  System time: 2019-04-16T08:46:11+03:00
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode:
|   2.02:
|_    Message signing enabled but not required
| smb2-time:
|   date: 2019-04-16 13:46:11
|_  start_date: N/A
```
Notes:
- There is an FTP, SSH, DNS, HTTP, HTTPS, and SMB service available
- The FTP service does not allow anonymous logins

---
## PART 2 : Port Enumeration

1. Explore __SMB__ service
   1. Enumeration
      ```console
      enum4linux -a 10.10.10.123
      ```
      ```
      ...

       ====================================================
      |    Enumerating Workgroup/Domain on 10.10.10.123    |
       ====================================================
      [+] Got domain/workgroup name: WORKGROUP

      ...

       =====================================
      |    Session Check on 10.10.10.123    |
       =====================================
      [+] Server 10.10.10.123 allows sessions using username '', password ''

      ...

       =========================================
      |    Share Enumeration on 10.10.10.123    |
       =========================================

              Sharename       Type      Comment
              ---------       ----      -------
              print$          Disk      Printer Drivers
              Files           Disk      FriendZone Samba Server Files /etc/Files
              general         Disk      FriendZone Samba Server Files
              Development     Disk      FriendZone Samba Server Files
              IPC$            IPC       IPC Service (FriendZone server (Samba, Ubuntu))
      Reconnecting with SMB1 for workgroup listing.

              Server               Comment
              ---------            -------

              Workgroup            Master
              ---------            -------
              WORKGROUP            FRIENDZONE

      [+] Attempting to map shares on 10.10.10.123
      //10.10.10.123/print$           Mapping: DENIED, Listing: N/A
      //10.10.10.123/Files            Mapping: DENIED, Listing: N/A
      //10.10.10.123/general          Mapping: OK, Listing: OK
      //10.10.10.123/Development      Mapping: OK, Listing: OK
      //10.10.10.123/IPC$             [E] Can't understand response:
      NT_STATUS_OBJECT_NAME_NOT_FOUND listing \*

      ...
      ```
      Notes:
      - Workgroup name is __WORKGROUP__
      - __/etc/Files__ was listed as comment for __Files__ share
      - __general__ and __Development__ shares does not require authentication
      
   1. Explore available __shares__
      1. //10.10.10.123/general
         ```console
         smbclient \\\\WORKGROUP\\general -I 10.10.10.123 -N
         ```
         - While inside the client:
           ```console
           dir
           # creds.txt      N     57  Wed Oct 10 07:52:42 2018
           get creds.txt
           ```
         - __creds.txt__ contents:
           ```
           creds for the admin THING:

           admin:WORKWORKHhallelujah@#
           ```
      1. //10.10.10.123/Development
         ```console
         smbclient \\\\WORKGROUP\\Development -I 10.10.10.123 -N
         ```
         - While inside the client:
           ```console
           dir
           ```
      Notes:
      - __general__ share contains __admin credentials__
      - __Development__ share is __empty__

2. Visit http://10.10.10.123
   - Page Source:
     ```html
     <title>Friend Zone Escape software</title>

     <center><h2>Have you ever been friendzoned ?</h2></center>

     <center><img src="fz.jpg"></center>

     <center><h2>if yes, try to get out of this zone ;)</h2></center>

     <center><h2>Call us at : +999999999</h2></center>

     <center><h2>Email us at: info@friendzoneportal.red</h2></center>
     ```
     Notes:
     - __friendzoneportal.red__ is a domain name

3. Do a DNS lookup for __friendzoneportal.red__ with _zone transfer_
   1. Enumeration:
      ```console
      dig @10.10.10.123 friendzoneportal.red axfr
      
      # friendzoneportal.red.         604800  IN     SOA     localhost. root.localhost. 2 604800 86400 2419200 604800
      # friendzoneportal.red.         604800  IN     AAAA    ::1
      # friendzoneportal.red.         604800  IN     NS      localhost.
      # friendzoneportal.red.         604800  IN     A       127.0.0.1
      # admin.friendzoneportal.red.   604800  IN     A       127.0.0.1
      # files.friendzoneportal.red.   604800  IN     A       127.0.0.1
      # imports.friendzoneportal.red. 604800  IN     A       127.0.0.1
      # vpn.friendzoneportal.red.     604800  IN     A       127.0.0.1
      # friendzoneportal.red.         604800  IN     SOA     localhost. root.localhost. 2 604800 86400 2419200 604800
      ```
   2. Add _subdomains_ to __/etc/hosts__
      ```
      127.0.0.1       localhost
      127.0.1.1       kali f
      10.10.10.123    friendzoneportal.red
      10.10.10.123    admin.friendzoneportal.red
      10.10.10.123    files.friendzoneportal.red    \\\DEAD END
      10.10.10.123    imports.friendzoneportal.red  \\\DEAD END
      10.10.10.123    vpn.friendzoneportal.red      \\\DEAD END

      # The following lines are desirable for IPv6 capable hosts
      ::1     localhost ip6-localhost ip6-loopback
      ff02::1 ip6-allnodes
      ff02::2 ip6-allrouters
      ```
4. Visit http://admin.friendzoneportal.red
   - Loads homepage of http://10.10.10.123
   
5. Visit http://10.10.10.123:443
   - HTTP Response
     ```
     <h1>Bad Request</h1>
     <p>Your browser sent a request that this server could not understand.<br />
     Reason: You're speaking plain HTTP to an SSL-enabled server port.<br />
     Instead use the HTTPS scheme to access this URL, please.<br />
     </p>
     <hr>
     <address>Apache/2.4.29 (Ubuntu) Server at 127.0.0.1 Port 443</address>
     ```
   - Switch to https://10.10.10.123
   - Check SSL Certificate
     ```console
     openssl s_client -connect 10.10.10.123:443 -quiet
     ```
     ```html
     depth=0 C = JO, ST = CODERED, L = AMMAN, O = CODERED, OU = CODERED, CN = friendzone.red, emailAddress = haha@friendzone.red
     verify error:num=18:self signed certificate
     verify return:1
     depth=0 C = JO, ST = CODERED, L = AMMAN, O = CODERED, OU = CODERED, CN = friendzone.red, emailAddress = haha@friendzone.red
     verify error:num=10:certificate has expired
     notAfter=Nov  4 21:02:30 2018 GMT
     verify return:1
     depth=0 C = JO, ST = CODERED, L = AMMAN, O = CODERED, OU = CODERED, CN = friendzone.red, emailAddress = haha@friendzone.red
     notAfter=Nov  4 21:02:30 2018 GMT
     verify return:1

     HTTP/1.1 400 Bad Request
     Date: Tue, 16 Apr 2019 08:57:42 GMT
     Server: Apache/2.4.29 (Ubuntu)
     Content-Length: 302
     Connection: close
     Content-Type: text/html; charset=iso-8859-1

     <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
     <html><head>
     <title>400 Bad Request</title>
     </head><body>
     <h1>Bad Request</h1>
     <p>Your browser sent a request that this server could not understand.<br />
     </p>
     <hr>
     <address>Apache/2.4.29 (Ubuntu) Server at 127.0.0.1 Port 443</address>
     </body></html>
     ```
   
     Notes:
     - __friendzone.red__ is another _domain name_
     - Try accessing subdomains over __https__

6. Visit https://admin.friendzoneportal.red
   - Page Source:
     ```html
     <title>Admin Page</title>

     <center><h2>Login and break some friendzones !</h2></center>

     <center><h2>Spread the love !</h2></center>

     <center>
     <form name="login" method="POST" action="login.php">

     <p>Username : <input type="text" name="username"></p>
     <p>Password : <input type="password" name="password"></p>
     <p><input type="submit" value="Login"></p>

     </form>
     </center>
     ```
   - Response after successful logging using credentials from __creds.txt__
     ```html
     <h1>Admin page is not developed yet !!! check for another one</h1>
     ```
   Notes:
   - Maybe there is another admin page in __friendzone.red__

7. Do a DNS lookup for __friendzone.red__ with _zone transfer_
   1. Enumeration:
      ```console
      dig @10.10.10.123 friendzone.red axfr
      
      # friendzone.red.                 604800  IN     SOA     localhost. root.localhost. 2 604800 86400 2419200 604800
      # friendzone.red.                 604800  IN     AAAA    ::1
      # friendzone.red.                 604800  IN     NS      localhost.
      # friendzone.red.                 604800  IN     A       127.0.0.1
      # administrator1.friendzone.red.  604800  IN     A       127.0.0.1
      # hr.friendzone.red.              604800  IN     A       127.0.0.1
      # uploads.friendzone.red.         604800  IN     A       127.0.0.1
      # friendzone.red.                 604800  IN     SOA     localhost. root.localhost. 2 604800 86400 2419200 604800
      ```
   2. Add _subdomains_ to __/etc/hosts__
      ```
      127.0.0.1       localhost
      127.0.1.1       kali f
      10.10.10.123    friendzone.red
      10.10.10.123    administrator1.friendzone.red
      10.10.10.123    hr.friendzone.red             \\\DEAD END
      10.10.10.123    uploads.friendzone.red        \\\DEAD END

      # The following lines are desirable for IPv6 capable hosts
      ::1     localhost ip6-localhost ip6-loopback
      ff02::1 ip6-allnodes
      ff02::2 ip6-allrouters
      ```
8. Visit https://administrator1.friendzone.red
   - Snippet from Page Source:
     ```html
     <form method="POST" action="login.php" name="Login" class="login-form">
       <input type="text" name="username" placeholder="username"/>
       <input type="password" name="password" placeholder="password"/>
       <button>login</button>
     </form>
     ```
   - Response after successful logging using credentials from __creds.txt__
     ```
     Login Done ! visit /dashboard.php
     ```
9. Go to https://administrator1.friendzone.red/dashboard.php
   - Page Source:
     ```html
     <title>FriendZone Admin !</title>
     <br><br><br>
     <center><h2>Smart photo script for friendzone corp !</h2></center>
     <center><h3>* Note : we are dealing with a beginner php developer and the application is not tested yet !</h3></center>        
     <br><br>
     <center><p>image_name param is missed !</p></center>
     <center><p>please enter it to show the image</p></center>
     <center><p>default is image_id=a.jpg&pagename=timestamp</p></center>
     ```
   - __/dashboard.php?image_id=a.jpg&pagename=timestamp__ 
     ```html
     <title>FriendZone Admin !</title>
     <br><br><br>
     <center><h2>Smart photo script for friendzone corp !</h2></center>
     <center><h3>* Note : we are dealing with a beginner php developer and the application is not tested yet !</h3></center>  
     <center>
       <img src='images/a.jpg'></center><center>
       <h1>Something went worng ! , the script include wrong param !</h1>
     </center>
     Final Access timestamp is 1555410914
     ```
   Notes:
   - The __image_id__ parameter is loaded from a directory __images/__
   - __pagename__ might be exploitable
---

## PART 3 : Generate User Shell

1. Exploit __pagename__ parameter from https://administrator1.friendzone.red/dashboard.php
