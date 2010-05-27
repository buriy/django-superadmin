from django.test.client import Client

class AdminFormTest(object):
    fixtures = []
    
    DATA = {}
    KEY = 'full_name'
    EDITED = 'edited_pk'
    
    BASE = None
    model = None  
    
    ADD = BASE + '/add/'
    EDIT = BASE + '/%s/'
    DELETE = BASE + '/%s/delete/'
     
    credentials = {'username': 'admin', 'password': 'admin'}
    
    def getKV(self):
        return {self.KEY: self.DATA[self.KEY]}
    
    def setUp(self):
        self.client = Client()
        if self.credentials:
            self.client.login(**self.credentials)
        
    def add(self):
        response = self.client.post(self.ADD, self.DATA)
        self.failUnlessEqual(response.status_code, 200)        

    def edit(self, pk):
        response = self.client.post(self.EDIT % pk, self.DATA)
        self.failUnlessEqual(response.status_code, 200)        

    def delete(self, pk):
        self.model._default_manager.get(pk=pk).delete()

    def ensure_added(self):
        try:
            return self.model._default_manager.get(**self.getKV()).pk
        except self.model.DoesNotExist:
            self.assert_(False)
            
    def ensure_deleted(self, pk):
        if self.model._default_manager.filter(pk=pk):
            self.assert_(False)
        
    def test_add(self):
        self.add()
        pk = self.ensure_added()
        self.delete(pk)
    
    def test_edit(self):
        self.add()
        pk = self.ensure_added()
        
        self.edit(pk)
        form = self.model._default_manager.get(pk=pk)
        
        self.assertEquals(getattr(form, self.KEY), self.EDITED)
        form.delete()
        
    def test_access(self):
        if self.credentials:
            self.client.logout()
            
            response = self.client.get('/')
            self.failUnlessEqual(response.status_code, 200) 
    
            #try without credentials
            response = self.client.get(self.ADD)
            self.failUnlessEqual(response.status_code, 302) #add
            
            response = self.client.get(self.EDIT % '1')
            self.failUnlessEqual(response.status_code, 302) #edit

            response = self.client.get(self.DELETE % '1')
            self.failUnlessEqual(response.status_code, 302) #delete

            self.client.login(**self.credentials)

        response = self.client.get(self.ADD)
        self.failUnlessEqual(response.status_code, 200) #add
        
        response = self.client.get(self.EDIT % '1')
        self.failUnlessEqual(response.status_code, 200) #edit

        response = self.client.get(self.DELETE % '1')
        self.failUnlessEqual(response.status_code, 200) #delete

    def test_delete(self):
        pk = self.add()
        self.client.post(self.DELETE % pk, {'delete': pk})
        self.ensure_deleted(pk)
