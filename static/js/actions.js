hexaa = new APIClient();

$(document).ready(function () {
    // ============================= Users ================================

    $('#group-member-search').on('keyup', function(e){
        var string = $(this).val();
        hexaa.users.search(string)
        .then((response)=>{
            var html = '';
            for(var user of response){
                html += '<option>' + user._id + '</option>'
            }
            $('#users-search-list').html(html);
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#edit-user-info").submit(function(){
        var data = $(this).getFormData();
        hexaa.users.updateInfo(data.firstname, data.lastname)
        .then((response)=>{
            window.location.reload()
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#edit-user-email").submit(function(){
        var data = $(this).getFormData();
        hexaa.users.updateEmail(data.email)
        .then((response)=>{
            window.location.reload()
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#edit-user-password").submit(function(){
        var data = $(this).getFormData();
        hexaa.users.updatePassword(data.old_password, data.new_password)
        .then((response)=>{
            window.location.reload()
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#edit-user-picture").submit(function(){
        var data = new FormData(this);
        hexaa.users.updateProfilePicture(data)
        .then((response)=>{
            window.location.reload()
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    // $('#custom-file-handler-picture').change(function(){ 
    //     var file = $(this).prop('files')[0];
    //     var fileReader = new FileReader();
    //     fileReader.readAsDataURL(file);
    //     fileReader.onload = function(e) {
    //         $('#picturePreview').attr('src', e.target.result);
    //     };
    //     $('#edit-user-picture').submit();
    // });
  
    // ============================= Groups ===============================

    $("#create-group-form").submit(function(){
        var data = $(this).getFormData();
        hexaa.groups.create(data.name, data.description)
        .then((response)=>{
            let url = '/groups/' + response.uid;
            window.location.href = url;
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#edit-group-form").submit(function(){
        var data = $(this).getFormData();
        hexaa.groups.update(data.group, data.name, data.description)
        .then((response)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#delete-group-form").submit(function(){
        var data = $(this).getFormData();
        hexaa.groups.delete(data.group)
        .then((response)=>{
            window.location.href = '/groups';
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#join-group-button").click(function(){
        var groupId = $(this).data('group');
        hexaa.groups.join(groupId)
        .then((response)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("button[name='acceptJoinRequest']").click(function(){
        var groupId = $(this).data('group');
        var requestId = $(this).data('request');
        hexaa.groups.acceptRequest(groupId, requestId)
        .then((response)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("button[name='rejectJoinRequest']").click(function(){
        var groupId = $(this).data('group');
        var requestId = $(this).data('request');
        hexaa.groups.rejectRequest(groupId, requestId)
        .then((response)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });
    
    
    // =========================== Memberships ============================

    $("#add-members-form").submit(function(){
        var data = $(this).getFormData();
        hexaa.groups.memberships.create(data.groupId, data.member, data.role)
        .then((data)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("button[name='updateMemberRole']").click(function(){
        var data = $(this).data();
        hexaa.groups.memberships.update(data.group, data.member, data.newrole)
        .then((data)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("button[name='removeMember']").click(function(){
        var data = $(this).data();
        hexaa.groups.memberships.delete(data.group, data.member)
        .then((data)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("button[name='leaveGroup']").click(function(){
        var data = $(this).data();
        hexaa.groups.memberships.delete(data.group, data.member)
        .then((data)=>{
            window.location.href = '/';
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    

    // =========================== Announcements ============================ 

    function editAnnouncement(announcementId){
        $("button[id^='announcementOptionsOf_']").prop('disabled', true);
        $("#announcementContentOf_"+ announcementId).attr('readonly', false);
        $("#announcementContentOf_"+ announcementId).attr('rows', '5');
        $("#announcementContentOf_"+ announcementId).addClass('border');
        $('#saveChangesOf_' + announcementId).show();
        $('#cancelChangesOf_' + announcementId).show();
    }

    function saveAnnouncementChanges(announcementId){
        $("button[id^='announcementOptionsOf_']").prop('disabled', false);
        $("#announcementContentOf_"+ announcementId).attr('readonly', true);
        $("#announcementContentOf_"+ announcementId).attr('rows', "auto");
        $("#announcementContentOf_"+ announcementId).removeClass('border');
        $('#saveChangesOf_' + announcementId).hide();
        $('#cancelChangesOf_' + announcementId).hide();
    }

    function cancelAnnouncementChanges(announcementId){
        $("button[id^='announcementOptionsOf_']").prop('disabled', false);
        $("#announcementContentOf_"+ announcementId).attr('readonly', true);
        $("#announcementContentOf_"+ announcementId).attr('rows', "auto");
        $("#announcementContentOf_"+ announcementId).removeClass('border');
        $('#saveChangesOf_' + announcementId).hide();
        $('#cancelChangesOf_' + announcementId).hide();
    }

    $("#create-announcements-form").submit(function(){
        var data = $(this).getFormData();
        hexaa.groups.announcements.create(data.groupId, data.content)
        .then((response)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });


    $("button[name='removeAnnouncement']").click(function(){
        var data = $(this).data();
        hexaa.groups.announcements.delete(data.group, data.announcement)
        .then((data)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("button[name='editAnnouncement']").click(function(){
        var data = $(this).data();
        editAnnouncement(data.announcement);
    });

    $("button[id^='saveChangesOf_']").click(function(){
        var data = $(this).data();
        var content = $('#announcementContentOf_' + data.announcement).val();

        hexaa.groups.announcements.update(data.group, data.announcement, content)
        .then((data)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        }).finally(()=>{
            saveAnnouncementChanges(data.announcement);
        });
        return false
    });

    $("button[id^='cancelChangesOf_']").click(function(){
        var data = $(this).data();
        cancelAnnouncementChanges(data.announcement);
    });

    // =========================== Assignments ============================    

    $("#create-assignment-form").submit(function(){
        var data = $(this).getFormData();
        hexaa.groups.assignments.create(data.groupId, data.name, data.description, data.deadline)
        .then((response)=>{
            let url = '/groups/' + data.groupId + '/assignments/' + response.uid;
            window.location.href = url;
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#publish-assignment-button").click(function(){
        var data = $(this).data();        
        hexaa.groups.assignments.publish(data.group, data.assignment)
        .then((resp)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#edit-assignment-form").submit(function(){
        var data = $(this).getFormData();
        hexaa.groups.assignments.update(data.groupId, data.assignmentId, data.name, data.description, data.deadline)
        .then((resp)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(JSON.stringify(error));
        });
        return false
    });

    $("#delete-assignment-form").submit(function(){
        var data = $(this).getFormData();
        hexaa.groups.assignments.delete(data.groupId, data.assignmentId)
        .then((resp)=>{
            let url = '/groups/' + data.groupId + '/assignments';
            window.location.href = url;
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });
   
    $("input[name='link-unlink-testsuite-checkbox']").change(function(){
        var is_checked = $(this).is(':checked');
        var data = $(this).data();
        if(is_checked){

            hexaa.groups.assignments.linkTestsuite(data.group, data.assignment, data.testsuite)
            .then((resp)=>{
                window.location.reload();
            }).catch((error)=>{
                alert(error.responseText);
            });

        }else{

            hexaa.groups.assignments.unlinkTestsuite(data.group, data.assignment, data.testsuite)
            .done((data)=>{
                window.location.reload();
            }).fail((error)=>{
                alert(error.responseText);
            });
        }
        return false
    });

    // =========================== Testsuites ============================

    $("#create-testsuite-form").submit(function(){
        var groupId = $(this).attr('group');
        var data = new FormData(this);
        hexaa.groups.testsuites.create(groupId, data)
        .then((response)=>{
            let url = '/groups/' + groupId + '/testsuites/' + response.uid;
            window.location.href = url;
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#edit-testsuite-form").submit(function(){
        var groupId = $(this).attr('group');
        var testsuiteId = $(this).attr('testsuite');
        var data = new FormData(this);
        hexaa.groups.testsuites.update(groupId, testsuiteId, data)
        .then((response)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#delete-testsuite-form").submit(function(){
        var data = $(this).getFormData();
        hexaa.groups.testsuites.delete(data.groupId, data.testsuiteId)
        .then((response)=>{
            let url = '/groups/' + data.groupId + '/testsuites';
            window.location.href = url;
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("#add-testcase-form").submit(function(){
        var data = $(this).getFormData();
        hexaa.groups.testsuites.addTestcase(data.group, data.testsuite, data.stdin, data.expected_stdout)
        .then((response)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false;
    });

    $("button[name='deleteTestcase']").click(function(){
        var data = $(this).data();
        hexaa.groups.testsuites.deleteTestcase(data.group, data.testsuite, data.testcase)
        .then((response)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("button[name='acceptTestcase']").click(function(){
        var data = $(this).data()
        hexaa.groups.testsuites.acceptTestcase(data.group, data.testsuite, data.testcase)
        .then((response)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

    $("button[name='rejectTestcase']").click(function(){
        var data = $(this).data()
        hexaa.groups.testsuites.rejectTestcase(data.group, data.testsuite, data.testcase)
        .then((response)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });  

    $("button[name='delete-testsuite-attachment']").click(function(){
        var data = $(this).data();
        hexaa.groups.testsuites.deleteAttachment(data.group, data.testsuite, data.attachment)
        .then((data)=>{
            window.location.reload();
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });
    
    // =========================== Submit code ==========================

    $("#submit-code-form").submit(function(){
        var data = $(this).data();
        var formData = new FormData(this);

        $('#submit-code').addClass('loading');
        $('#submit-code').prop( "disabled", true);

        hexaa.groups.assignments.submit(data.group, data.assignment, formData)
        .then((response) =>{
            return response;
        })
        .then((response)=>{
            window.location.href = '/submissions/' + response.uid;
        }).catch((error)=>{
            alert(error.responseText);
        })
        .then(()=>{
            $('#submit-code').removeClass('loading');
            $('#submit-code').prop('disabled', false);  
        });
        return false;
    });

    $("a[name='downloadfile']").click(function(){
        var data = $(this).data();
        hexaa.groups.assignments.downloadFile(data.submission)
        .then((data)=>{
            window.location.href = data.url;
        }).catch((error)=>{
            alert(error.responseText);
        });
        return false
    });

});