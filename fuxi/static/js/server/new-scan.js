$(function () {
    var demo1 = $('select[name="plugin_list"]').bootstrapDualListbox();

    $("#showConfig").click(function () {
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
                "source": "scan_view",
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
});