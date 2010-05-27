def patch_admin_auth():
    import auth #@UnusedImport

def patch_autosuperuser():
    import syncdb #@UnusedImport

def patch_editrelated():
    import editrelated #@UnusedImport

def patch_everything():
    patch_admin_auth()
    patch_autosuperuser()
    patch_editrelated()
