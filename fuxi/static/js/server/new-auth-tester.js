function showSelect(){
    document.getElementById("post_data_inner").innerHTML="";
    document.getElementById("get_data_inner").innerHTML="";
    const select = $('[id="http_auth_select_id"]').val();
    if(select==='1'){
        document.getElementById("post_data_inner").innerHTML="";
        document.getElementById("basic_data_inner").innerHTML="";
        document.getElementById("get_data_inner").innerHTML="<label class='control-label col-md-2'>GET Date<span class='text-danger'>*</span></label>" +
            "<div class='col-md-6'><textarea class='form-control' placeholder='Example: http://www.example.com/login.jsp?username=[zhangsan]&password=[123456]' name='get_auth_data'></textarea></div>";
    } else if (select==='2'){
        document.getElementById("get_data_inner").innerHTML="";
        document.getElementById("basic_data_inner").innerHTML="";
        document.getElementById("post_data_inner").innerHTML="<label class='control-label col-md-2'>POST Date<span class='text-danger'>*</span></label>" +
            "<div class='col-md-6'><textarea class='form-control' rows='6' placeholder='' name='post_auth_data'></textarea></div>";
    } else if (select==='0') {
        document.getElementById("post_data_inner").innerHTML="";
        document.getElementById("get_data_inner").innerHTML="";
        document.getElementById("basic_data_inner").innerHTML="<label class='control-label col-md-2'>Target<span class='text-danger'>*</span></label>" +
            "<div class='col-md-6'><textarea class='form-control' rows='6' placeholder='Example: http://192.168.1.1 (One target per line)' name='basic_auth_data'></textarea></div>";
    }
}

$(function () {
    $(".new_http_test").click(function () {
        const select = $('[id="http_auth_select_id"]').val();
        if(select==='0') {
            const task_name = $('[name="http_task_name"]').val();
            const target_val = $('[name="basic_auth_data"]').val();
            const username_val = $('[name="http_username_val"]').val();
            const password_val = $('[name="http_password_val"]').val();
            const recursion = $('[name="http_recursion"]').val();
            if (!task_name || !target_val || !username_val || !password_val) {
                swal("Warning","Please check the input!", "error");
            } else {
                $.post('/auth-tester', {
                    "task_name": task_name,
                    "target_val": target_val,
                    "username_val": username_val,
                    "password_val": password_val,
                    "recursion": recursion,
                    "source": "basic_auth"
            }, function (e) {
                    if (e === 'success') {
                        swal({
                            title: "Task added successfully!",
                            text: "",
                            type: "success",
                            confirmButtonColor: "#41b883",
                            confirmButtonText: "ok",
                            closeOnConfirm: false
                        },
                            function(){
                            location.href = "/auth-tester-tasks";
                        });
                    } else {
                        swal("Error","Something wrong", "error");
                    }
                })
            }
        }
    });

    $(".new_mysql_test").click(function () {
        const task_name = $('[name="mysql_task_name"]').val();
        const target_val = $('[name="mysql_target_data"]').val();
        const username_val = $('[name="mysql_username_val"]').val();
        const password_val = $('[name="mysql_password_val"]').val();
        const recursion = $('[name="mysql_recursion"]').val();
        if (!task_name || !target_val || !username_val || !password_val) {
            swal("Warning","Please check the input!", "error");
        } else {
            $.post('/auth-tester', {
                "task_name": task_name,
                "target_val": target_val,
                "username_val": username_val,
                "password_val": password_val,
                "recursion": recursion,
                "source": "mysql_auth"
        }, function (e) {
                if (e === 'success') {
                    swal({
                        title: "Success Create!",
                        text: "",
                        type: "success",
                        confirmButtonColor: "#41b883",
                        confirmButtonText: "ok",
                        closeOnConfirm: false
                    },
                        function(){
                        location.href = "/auth-tester-tasks";
                    });
                } else {
                    swal("Error","Something wrong", "error");
                }
            })
        }
    });

    $(".new_ssh_test").click(function () {
        const task_name = $('[name="ssh_task_name"]').val();
        const target_val = $('[name="ssh_target_data"]').val();
        const username_val = $('[name="ssh_username_val"]').val();
        const password_val = $('[name="ssh_password_val"]').val();
        const recursion = $('[name="ssh_recursion"]').val();
        if (!task_name || !target_val || !username_val || !password_val) {
            swal("Warning","Please check the input!", "error");
        } else {
            $.post('/auth-tester', {
                "task_name": task_name,
                "target_val": target_val,
                "username_val": username_val,
                "password_val": password_val,
                "recursion": recursion,
                "source": "ssh_auth"
        }, function (e) {
                if (e === 'success') {
                    swal({
                        title: "Task added successfully!",
                        text: "",
                        type: "success",
                        confirmButtonColor: "#41b883",
                        confirmButtonText: "ok",
                        closeOnConfirm: false
                    },
                        function(){
                        location.href = "/auth-tester-tasks";
                    });
                } else {
                    swal("Error","Something wrong", "error");
                }
            })
        }
    });

    $(".new_redis_test").click(function () {
        const task_name = $('[name="redis_task_name"]').val();
        const target_val = $('[name="redis_target_data"]').val();
        const password_val = $('[name="redis_password_val"]').val();
        const recursion = $('[name="redis_recursion"]').val();
        if (!task_name || !target_val || !password_val) {
            swal("Warning","Please check the input!", "error");
        } else {
            $.post('/auth-tester', {
                "task_name": task_name,
                "target_val": target_val,
                "username_val": "None",
                "password_val": password_val,
                "recursion": recursion,
                "source": "redis_auth"
        }, function (e) {
                if (e === 'success') {
                    swal({
                        title: "Success Create!",
                        text: "",
                        type: "success",
                        confirmButtonColor: "#41b883",
                        confirmButtonText: "ok",
                        closeOnConfirm: false
                    },
                        function(){
                        location.href = "/auth-tester-tasks";
                    });
                } else {
                    swal("Error","Something wrong", "error");
                }
            })
        }
    });

    $(".username-update").click(function () {
        const username_dict = $('[name="edit_username_val"]').val();
        if (!username_dict) {
            swal("Warning","Please check the input!", "error");
        } else {
            $.post('/advanced-option', {
                "username_dict": username_dict,
                "source": "auth_username"
            }, function (e) {
                if (e === 'success') {
                    swal({
                      title: "Updated successfully!",
                      text: "",
                      type: "success",
                      confirmButtonColor: "#41b883",
                      confirmButtonText: "ok",
                      closeOnConfirm: false
                    },
                    function(){
                      location.href = "/new-auth-tester";
                    });
                } else {
                    swal("Error","Something wrong", "error");
                }
            })
        }
    });

    $(".password-update").click(function () {
        const password_dict = $('[name="edit_password_val"]').val();
        if (!password_dict) {
            swal("Warning","Please check the input!", "error");
        } else {
            $.post('/advanced-option', {
                "password_dict": password_dict,
                "source": "auth_password"
            }, function (e) {
                if (e === 'success') {
                    swal({
                      title: "Successfully Update!",
                      text: "",
                      type: "success",
                      confirmButtonColor: "#41b883",
                      confirmButtonText: "ok",
                      closeOnConfirm: false
                    },
                    function(){
                      location.href = "/new-auth-tester";
                    });
                } else {
                    swal("Error","Something wrong", "error");
                }
            })
        }
    });
});
