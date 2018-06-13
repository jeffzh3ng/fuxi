$(function () {
    $('#sampleTable').DataTable();


    $(".task-update").click(function () {
        const taskname_val = $('[name="taskname_val"]').val();
        const task_id = $('[name="task_id"]').val();
        const recursion_val = $('[name="recursion_val"]').val();
        const target_val = $('[name="target_val"]').val();
        if (!taskname_val || !task_id || !target_val) {
            swal("Warning","Please check the input!", "error");
        } else {
            $.post('/task-edit', {
                "taskname_val": taskname_val,
                "task_id": task_id,
                "recursion_val": recursion_val,
                "target_val": target_val,
            }, function (e) {
                if (e === 'success') {
                    swal({
                      title: "Updated Successfully!",
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
                    swal("Error","Something wrong", "error");
                }
            })
        }
    });
});

function rescan_task(nid){
    const data = {
        "rescan": nid,
    };
    swal({
      title: "Are you sure want to rescan?",
      text: "This will clear the scan result！",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Rescan",
      closeOnConfirm: false
    },
    function(){
        $.ajax({
            type: 'GET',
            url: '/task-management',
            data: data,
            success: function() {
                location.href = "/task-management";
                },
            error: function(xhr, type) {
            }
        });
    });
}

function task_edit_id(nid){
    const data = {
        "edit": nid,
    };
    $.ajax({
        type: 'GET',
        url: '/task-management',
        data: data,
        dataType: 'json',
        success: function(e) {
            const data  = eval(e);
            const task_name = data.task_name;
            const scan_target_list = data.scan_target;
            $('#scan_target_list').val(scan_target_list);
            $('#task_name').val(task_name);
            $('#task_id').val(nid);
        },
        error: function(xhr, type) {
        }
    });
}

function task_delete(nid){
    const data = {
        "delete": nid,
    };
    swal({
      title: "Are you sure you want to delete?",
      text: "",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Delete！",
      closeOnConfirm: false
    },
    function(){
        $.ajax({
            type: 'GET',
            url: '/task-management',
            data: data,
            success: function() {
                location.href = "/task-management";
                },
            error: function(xhr, type) {
            }
        });
    });
}
