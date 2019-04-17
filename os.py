infile = open("/root/root.txt", "r").read()
outfile = open("/tmp/something", "w").write(infile)
outfile.close()
