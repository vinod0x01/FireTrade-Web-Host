//variables to validate
var email_val = false;
var passwor_val = false;
var name_val = false;
//validating function
$(document).ready(function() {
  $("#disp-name").change(function() {
    var d = document.getElementById("disp-name").value;
    if (!/^([a-zA-Z]+\w*){5,20}$/g.test(d)) {
      $("#err_name")
        .text(
          "name should be 5 to 20 charecteres\nonly digits or letters or _\nstart with letter"
        )
        .show();
      name_val = false;
    } else {
      $("#err_name")
        .text("")
        .show();
      name_val = true;
    }
  });
  $("#email").change(function() {
    var d = document.getElementById("email").value;
    if (!/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(d)) {
      $("#err_mail")
        .text("enter a valid mail")
        .show()
        .fadeOut(2000);
      email_val = false;
    } else {
      email_val = true;
    }
  });
  $(":password").change(function() {
    var d = document.getElementById("password").value;
    if (!/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,20}$/.test(d)) {
      $("#err_pass")
        .text(
          "password should be 6 to 20 characters which contain at least one numeric digit, one uppercase and one lowercase letter"
        )
        .show()
        .fadeOut(5000);
      passwor_val = false;
    } else {
      passwor_val = true;
    }
  });
});

//function to verify the email and call sign in from python via post request
function email_verify() {
  var email = document.getElementById("email").value;
  var pass = document.getElementById("password").value;
  var errorCode = new String();
  var errorMessage = new String();
  if (email == "") {
    $("#err_mail")
      .text("*email cannot be empty")
      .show()
      .fadeOut(2000);
    return;
  } else if (pass == "") {
    $("#err_pass")
      .text("*password cannot be empty")
      .show()
      .fadeOut(2000);
    return;
  } else {
    var data = {
      email: email,
      password: pass
    };
    //post request from jquery to the python
    $.ajax({
      type: "POST",
      url: "/login",
      data: data,
      cache: false,
      success: function(resp) {
        if (resp.result) {
          if (resp.result == "failed") {
            $("#err_pass")
              .text(resp.msg)
              .show()
              .fadeOut(4000);
          }
          if (resp.result == "success") {
            window.location.href = resp.url;
          }
        } else {
          $("#err_pass")
            .text("Something went wrong")
            .show()
            .fadeOut(4000);
        }
      },
      error: function(request, status, error) {
        $("#err_pass")
          .text(status)
          .show()
          .fadeOut(4000);
      }
    });
  }
}

//function for signing in
function sign_in() {
  if (!email_val || !passwor_val || !name_val) {
    $("#err_pass")
      .text("Please enter a valid email and password and name")
      .show()
      .fadeOut(2000);
  } else {
    var name = document.getElementById("disp-name").value;
    var mail = document.getElementById("email").value;
    var pass = document.getElementById("password").value;
    var data = {
      name: name,
      email: mail,
      password: pass
    };
    //post request to python to create a new user
    $.ajax({
      type: "POST",
      url: "/create_user",
      data: data
    }).done(function(resp) {
      if (resp.result == "success") {
        $(":input").val("");
        $("#mseg")
          .text(
            "verification mail sent to " +
              resp.msg +
              " please confirm e-mail and login again"
          )
          .show();
      } else if (resp.result == "failed") {
        $("#err_pass")
          .text(resp.msg)
          .show()
          .fadeOut(2000);
      }
    });
  }
}
