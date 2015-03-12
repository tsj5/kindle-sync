#!/usr/bin/env python


import os, shutil, sqlite3

# Come up with an abbreviated author/title/year string to use as filename on Kindle
def kindle_name(pub, source):
    if "pdf" in source["mime_type"]:
       suffix = ".pdf"
    elif "djvu" in source["mime_type"]:
       suffix = ".djvu"
    else:
       suffix = source["path"].rpartition(".")[2]

    if pub["type"] == 0: #Papers2 "Book" category

        #if pub["summary"].find("short_name=") == -1
        #    title = pub["summary"]
        #    authors = ""

        if pub["author_string"] is not '':
            au_string = pub["author_string"]
        else:
            au_string = pub["editor_string"]

    else: # Journal article, basically
        if pub["author_year_string"].startswith("Anon."):
            au_string = pub["author_year_string"] 
        else:
            au_string = "(" + pub["publication_date"][2:6] + ")" # publication year only

    return au_string + ' - ' + pub["title"].partition(":")[0] + suffix


# Process all files and collections contained in a given collection
def recurse_on_collection(cursor, coll_dict, parent_dir):

    print coll_dict["name"]
    this_dir = os.path.join(parent_dir, coll_dict["name"])
    if not os.path.exists(this_dir):
        try:
            os.mkdir(this_dir)
        except os.error, why:
            print "Couldn't make directory"
            return
    os.chdir(this_dir)

    # Copy over all publications we find in this collection
    cursor.execute("SELECT object_id FROM CollectionItem WHERE collection = ?;", 
                   (coll_dict["ROWID"],))
    pub_ids = cursor.fetchall()
    #TODO: if any pubs in a collection are flagged, copy only the flagged ones
    for id in pub_ids:
        cursor.execute("SELECT * FROM Publication WHERE ROWID = ?;", 
                       (id["object_id"],))
        pub_info = cursor.fetchone()
        cursor.execute("SELECT path, mime_type FROM PDF WHERE object_id = ?;", 
                       (id["object_id"],))
        source = cursor.fetchone()
        dest_filename = kindle_name(pub_info, source)
        if not os.path.exists(dest_filename):
            try:
                shutil.copy2(os.path.join(libpath, source["path"]), 
                             dest_filename)
            except os.error, why:
                print "Couldn't copy file"

    #Look for subcollections & if found, recurse
    cursor.execute("SELECT ROWID, name FROM Collection WHERE parent = ?;", (coll_dict["ROWID"],))
    subcolls = cursor.fetchall()
    if len(subcolls) == 0:
        return
    else:
        for subcoll_dict in subcolls:
            recurse_on_collection(cursor, subcoll_dict, this_dir) 



# the script itself
libpath = "/Users/tsj/Documents/Papers2"
dbpath = "Library.papers2/Database.papersdb"
kpath = "/Volumes/Kindle/documents"

db_connection = sqlite3.connect(os.path.join(libpath,dbpath))

with db_connection:
    db_connection.row_factory = sqlite3.Row
    cursor = db_connection.cursor()
    try:
        cursor.execute("SELECT * FROM metadata LIMIT 1;")
    except sqlite3.OperationalError:
        raise ValueError("Invalid Papers database")

    cursor.execute("SELECT ROWID, name FROM Collection WHERE name LIKE '~ %';") # Doesn't like nonASCII
    root_colls = cursor.fetchall()
    if not(len(root_colls) == 0):
        for coll_dict in root_colls:
            recurse_on_collection(cursor, coll_dict, kpath) 





# def author_string(cursor, publication_ROWID):
#     cursor.execute("SELECT author_id FROM OrderedAuthor WHERE object_id = ? ORDER BY priority ASC;", (publication_ROWID,))
#     author_ids = cursor.fetchall()
#     au_list = []
#     for author in author_ids:
#         cursor.execute("SELECT surname FROM Author WHERE ROWID = ?;", (author["author_id"],))
#         au_list.append(cursor.fetchone["surname"])
#     if len(au_list) == 0:
#         pass
#     elif len(aulist) == 1:
#         pass
#     elif len(aulist) == 2:
#         pass
#     elif len(aulist) == 3:
#         pass
#     else
#         return foo

