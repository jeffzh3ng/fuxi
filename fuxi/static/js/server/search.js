var demo1 = $('select[name="plugin_list"]').bootstrapDualListbox();

$(".btn_select").on("click",function(){
    var selects = document.getElementsByName("select_id");
    if($(this).attr("rel")==="select_all"){
        document.getElementById( "btn_select" ).rel = "unselect_all";
        document.getElementById( "btn_select" ).innerHTML = "Unselect All";
        for(var i = 0; i < selects.length; ++i)
        {
            selects[i].checked = true;
        }
    }else if($(this).attr("rel")==="unselect_all"){
        document.getElementById( "btn_select" ).rel = "select_all";
        document.getElementById( "btn_select" ).innerHTML = "Select All";
        for(var i = 0; i < selects.length; ++i)
        {
            selects[i].checked = false;
        }
    }
});

$("#asset-auth-tasks").click(function () {
    const username_list = $('[name="username_val"]').val();
    const password_list = $('[name="password_val"]').val();
    const task_name = $('[name="auth_taskname_val"]').val();
    const target_list = $('[name="auth_target_list"]').val();
    const recursion = $('[name="auth_recursion"]').val();
    const auth_type = $('[name="auth_type"]').val();
    if (!username_list || !password_list || !task_name || !target_list || !recursion || !auth_type) {
        swal("Warning","Please check the input!", "error");
    } else {
        $.post('/new-auth-task', {
            "username_list": username_list,
            "password_list": password_list,
            "task_name": task_name,
            "target_list": target_list,
            "recursion": recursion,
            "auth_type": auth_type,
            "source": "asset",
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
                swal("Warning","Failed to create task!", "error");
            }
        })
    }
});

$("#server-scan").click(function () {
    const taskname_val = $('[name="taskname_val"]').val();
    const plugin_val = $('[name="plugin_list"]').val().join(",");
    const recursion_val = $('[name="recursion_val"]').val();
    const target_val = $('[name="target_val"]').val();
    if (!taskname_val || !plugin_val || !target_val) {
        swal("Warning","Please check the input!", "error");
    } else {
        $.post('/add-task', {
            "taskname_val": taskname_val,
            "plugin_val": plugin_val,
            "recursion_val": recursion_val,
            "target_val": target_val,
            "source": "asset",
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
                  location.href = "/task-management";
                });
            } else {
                swal("Warning","Failed to create task!", "error");
            }
        })
    }
});

function newServiceScan() {
    var select_list = [];
    $("input[name='select_id']:checked").each(function () {
        select_list.push(this.value);
    });
    if(select_list.length === 0) {
        swal("Warning","Please select the target", "error");
    } else {
        $('#scan_target_list').val(select_list.join("\n"))
    }
}

function newAuthTester() {
    var select_list = [];
    $("input[name='select_id']:checked").each(function () {
        select_list.push(this.value);
    });
    if(select_list.length === 0) {
        swal("Warning","Please select the target", "error");
    } else {
        $('#auth_target_list').val(select_list.join("\n"))
    }
}
