function APIClient() {
    this.base_url = '/api/';   
    this.users = new User(this); 
    this.groups = new Group(this);  
    this.call_api = function(url, type=null, data=null, contentType=null, dataType=null){
        var xhr = $.ajax({
            url:  this.base_url + url,
            type: type,        
            data: data,
            dataType: dataType,
            contentType: contentType || false,
            processData: false,
            cache: false,
        });
        return xhr;
    };
}

function User(client) {
    this.client = client;
    this.memberships = new Membership(client);
    this.assignments = new Assignment(client);
    this.testsuites = new Testsuite(client);

    // method for GET /users/search
    this.search = function(string){
        let url = 'users/search?q=' + string;
        let dataType = 'json';
        return this.client.call_api(url, 'get', null, null, dataType);
    }
    // method for PUT /user/name
    this.updateInfo = function(firstname, lastname){
        let url = 'user/name';
        let contentType = 'application/json';
        let data = {'firstname':firstname, 'lastname':lastname};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'put', body, contentType);
    }
    // method for PUT /user/email
    this.updateEmail = function(email){
        let url = 'user/email';
        let contentType = 'application/json';
        let data = {'email':email};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'put', body, contentType);
    }
    // method for PUT /user/password
    this.updatePassword = function(old_password, new_password){
        let url = 'user/password';
        let contentType = 'application/json';
        let data = {'old_password':old_password, 'new_password':new_password};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'put', body, contentType);
    }
    // method for PUT /user/pciture
    this.updateProfilePicture = function(data){
        let url = 'user/picture';
        return this.client.call_api(url, 'put', data);
    }
}

function Group(client) {
    this.client = client;
    this.memberships = new Membership(client);
    this.assignments = new Assignment(client);
    this.announcements = new Announcement(client);
    this.testsuites = new Testsuite(client);

    // method for GET /groups
    this.list = function(){
        let url = 'groups';
        let dataType = 'json';
        return this.client.call_api(url, 'get', null, null, dataType);
    }
    // method for GET /groups/<groupId>    
    this.get = function(groupId){
        let url = 'groups/' + groupId;
        let dataType = 'json';
        return this.client.call_api(url, 'get', null, null, dataType);
    }
    // method for POST /groups
    this.create = function(name, description=null){
        let url = 'groups';
        let contentType = 'application/json';
        let dataType = 'json';
        let data = {'name':name, 'description':description};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'post', body, contentType, dataType);
    }
    // method for PUT /groups/<groupId>
    this.update = function(groupId, name, description=null){
        let url = 'groups/' + groupId;
        let contentType = 'application/json';        
        let data = {'name':name, 'description':description};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'put', body, contentType);
    }
    // method for DELETE /groups/<groupId>
    this.delete = function(groupId){
        let url = 'groups/' + groupId;
        return this.client.call_api(url, 'delete');
    }
    // method for POST /groups/<groupId>/join
    this.join = function(groupId){
        let url = 'groups/' + groupId + '/join';
        return this.client.call_api(url, 'post');
    }
    // method for POST /groups/<groupId>/request/<requestId>
    this.acceptRequest = function(groupId, requestId){
        let url = 'groups/' + groupId + '/requests/' + requestId;
        return this.client.call_api(url, 'post');
    }
     // method for DELETE /groups/<groupId>/request/<requestId>
     this.rejectRequest = function(groupId, requestId){
        let url = 'groups/' + groupId + '/requests/' + requestId;
        return this.client.call_api(url, 'delete');
    }
}

function Membership(client){
    this.client = client
    // method for GET /groups/<groupId>/members    
    this.list = function(groupId){
        let url = 'groups/' + groupId + '/members';
        let dataType = 'json';
        return this.client.call_api(url, 'get', null, null, dataType);
    }
    // method for POST /groups/<groupId>/members    
    this.create = function(groupId, member, role='member'){
        let url = 'groups/' + groupId + '/members';
        let contentType = 'application/json'; 
        let data = {'member':member, 'role':role};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'post', body, contentType);
    }
    // method for PUT /groups/<groupId>/members/<member>    
    this.update = function(groupId, member, role){
        let url = 'groups/' + groupId + '/members/' + member;
        let contentType = 'application/json'; 
        let data = {'role':role};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'put', body, contentType);
    }
    // method for DELETE /groups/<groupId>/members/<member>    
    this.delete = function(groupId, member){
        let url = 'groups/' + groupId + '/members/' + member;
        return this.client.call_api(url, 'delete');
    }
}

function Announcement(client) {
    this.client = client;

    // method for GET /groups/<groupId>/announcements
    this.list = function(groupId){
        let url = 'groups/' + groupId + '/announcements';
        let dataType = 'json';
        return this.client.call_api(url, 'get', null, null, dataType);
    }
    // method for POST /groups/<groupId>/announcements    
    this.create = function(groupId, content){
        let url = 'groups/' + groupId + '/announcements';
        let contentType = 'application/json'; 
        let dataType = 'json';
        let data = {'content':content};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'POST',  body, contentType, dataType);
    }
    // method for PUT /groups/<groupId>/announcements/<announcementId> 
    this.update = function(groupId, announcementId, content){
        let url = 'groups/' + groupId + '/announcements/' + announcementId;
        let contentType = 'application/json'; 
        let data = {'content':content};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'put', body, contentType);
    }
    // method for DELETE /groups/<groupId>/announcements/<announcementId>    
    this.delete = function(groupId, announcementId){
        let url = 'groups/' + groupId + '/announcements/' + announcementId;
        return this.client.call_api(url, 'delete');
    }
}

function Assignment(client) {
    this.client = client
    // method for GET /groups/<groupId>/assignments
    this.list = function(groupId){
        let url = 'groups/' + groupId + '/assignments';
        let dataType = 'json';
        return this.client.call_api(url, 'get', null, null, dataType);
    }
    // method for GET /groups/<groupId>/assignments/<assignmentId>    
    this.get = function(groupId, assignmentId){
        let url = 'groups/' + groupId + '/assignments/' + assignmentId;
        let dataType = 'json';
        return this.client.call_api(url, 'get', null, null, dataType);
    }
    // method for POST /groups/<groupId>/assignments/<assignmentId>/publish
    this.publish = function(groupId, assignmentId){
        let url = 'groups/' + groupId + '/assignments/' + assignmentId + '/publish';
        return this.client.call_api(url, 'post');
    }
    // method for POST /groups/<groupId>/assignments    
    this.create = function(groupId, name, description=null, deadline=null){
        let url = 'groups/' + groupId + '/assignments';
        let contentType = 'application/json'; 
        let dataType = 'json';
        let data = {'name':name, 'description':description, 'deadline':deadline};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'POST',  body, contentType, dataType);
    }
    // method for PUT /groups/<groupId>/assignments/<assignmentId> 
    this.update = function(groupId, assignmentId, name, description=null, deadline=null){
        let url = 'groups/' + groupId + '/assignments/' + assignmentId;
        let contentType = 'application/json'; 
        let data = {'name':name, 'description':description, 'deadline':deadline};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'put', body, contentType);
    }
    // method for DELETE /groups/<groupId>/assignments/<assignmentId>    
    this.delete = function(groupId, assignmentId){
        let url = 'groups/' + groupId + '/assignments/' + assignmentId;
        return this.client.call_api(url, 'delete');
    }
    // method for POST /groups/<groupId>/assignments/<assignmentId>/testsuites    
    this.linkTestsuite = function(groupId, assignmentId, testsuiteId){
        let url = 'groups/' + groupId + '/assignments/' + assignmentId + '/testsuites';
        let contentType = 'application/json'; 
        let data = {'testsuiteId':testsuiteId};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'post', body, contentType);
    }
    // method for DELETE /groups/<groupId>/assignments/<assignmentId>/testsuites/<testsuiteId>    
    this.unlinkTestsuite = function(groupId, assignmentId, testsuiteId){
        let url = 'groups/' + groupId + '/assignments/' + assignmentId + '/testsuites/' + testsuiteId;
        return this.client.call_api(url, 'delete');
    }
    // method for POST /groups/<groupId>/assignments/<assignmentId>/submit 
    this.submit = function(groupId, assignmentId, data){
        let url = 'groups/' + groupId + '/assignments/' + assignmentId + '/submit';
        let dataType = 'json';
        return this.client.call_api(url, 'post', data, null, dataType);
    }
}

function Testsuite(client) {
    this.client = client
    // method for GET /groups/<groupId>/testsuites    
    this.list = function(groupId){
        let url = 'groups/' + groupId + '/testsuites';
        let dataType = 'json';
        return this.client.call_api(url, 'get', null, null, dataType);
    }
    // method for GET /groups/<groupId>/testsuites/<testsuiteId>    
    this.get = function(groupId, testsuiteId){
        let url = 'groups/' + groupId + '/testsuites/' + testsuiteId;
        let dataType = 'json';
        return this.client.call_api(url, 'get', null, null, dataType);
    }
    // method for POST /groups/<groupId>/testsuites    
    this.create = function(groupId, data){
        let url = 'groups/' + groupId + '/testsuites';
        let dataType = 'json';
        return this.client.call_api(url, 'post', data, null, dataType);
    }
    // method for PUT /groups/<groupId>/testsuites/<testsuiteId>    
    this.update = function(groupId, testsuiteId, name, level, public, attempts){
        let url = 'groups/' + groupId + '/testsuites/' + testsuiteId;
        let contentType = 'application/json'; 
        let data = {'name':name, 'level':level, 'public':public, 'attempts':attempts};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'put', body, contentType);
    }
    // method for DELETE /groups/<groupId>/testsuites/<testsuiteId>    
    this.delete = function(groupId, testsuiteId){
        let url = 'groups/' + groupId + '/testsuites/' + testsuiteId;
        return this.client.call_api(url, 'delete');
    }
    // method for POST /groups/<groupId>/testsuites/<testsuiteId>/testcases
    this.addTestcase = function(groupId, testsuiteId, stdin, expected_stdout){
        let url = 'groups/' + groupId + '/testsuites/' + testsuiteId + '/testcases';
        let contentType = 'application/json'; 
        let dataType = 'json';
        let data = {'stdin':stdin, 'expected_stdout':expected_stdout};
        let body = JSON.stringify(data);
        return this.client.call_api(url, 'post', body, contentType, dataType);
    }
    // method for DELETE /groups/<groupId>/testsuites/<testsuiteId>/testcases/<testcaseId>
    this.deleteTestcase = function(groupId, testsuiteId, testcaseId){
        let url = 'groups/' + groupId + '/testsuites/' + testsuiteId + '/testcases/' + testcaseId;
        return this.client.call_api(url, 'delete');
    }
    // method for POST /groups/<groupId>/testsuites/<testsuiteId>/testcases/<testcaseId>/accept
    this.acceptTestcase = function(groupId, testsuiteId, testcaseId){
        let url = 'groups/' + groupId + '/testsuites/' + testsuiteId + '/testcases/' + testcaseId + '/accept';
        return this.client.call_api(url, 'post');
    }
    // method for DELETE /groups/<groupId>/testsuites/<testsuiteId>/testcases/<testcaseId>/reject
    this.rejectTestcase = function(groupId, testsuiteId, testcaseId){
        let url = 'groups/' + groupId + '/testsuites/' + testsuiteId + '/testcases/' + testcaseId + '/reject';
        return this.client.call_api(url, 'delete');
    }
}