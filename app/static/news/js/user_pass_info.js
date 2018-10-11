function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();

        // TODO 修改密码
        var params = {};
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value;
        });

        // 取到两次密码进行判断
        var new_password = params["new_password"];
        var confirm_password = params["confirm_password"];

        if (new_password != confirm_password) {
            alert("两次密码输入不一致");
            return
        }

        $.ajax({
            url: "/profile/pass_info",
            type: "POST",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 修改成功
                    alert("修改成功");
                    window.location.reload()
                } else {
                    alert(resp.errmsg)
                }
            }
        })

    })
});