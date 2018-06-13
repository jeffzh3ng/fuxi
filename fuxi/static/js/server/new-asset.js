$(function () {
    $("#newAsset").click(function () {
        const asset_name = $('[name="asset_name"]').val();
        const asset_host = $('[name="asset_host"]').val();
        const dept_name = $('[name="dept_name"]').val();
        const admin_name = $('[name="admin_name"]').val();
        const discover_option = $("input[type='checkbox']").is(':checked');
        if (!asset_name || !asset_host) {
            swal("Warning","Please check the input!", "error");
        } else {
            $.post('/new-asset', {
                "asset_name": asset_name,
                "asset_host": asset_host,
                "dept_name": dept_name,
                "admin_name": admin_name,
                "discover_option": discover_option,
                "source": "new_asset",
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
                      location.href = "/asset-management";
                    });
                } else {
                    swal("Warning","Failed to create asset!", "error");
                }
            })
        }
    });
});