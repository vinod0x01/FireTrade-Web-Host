//function to get the list of selected items
function select_items() {
  var opt = {};
  var x = $("#selector1").val();
  var itr, item;
  if (x.length < 5) {
    $("#err_msg")
      .text("Please select 5 options")
      .show();
    return;
  }
  $("#load_btn").css("display", "block");
  x.forEach(function(val, index) {
    opt[index] = val;
  });
  //post request to the python to predict based on selection
  $.ajax({
    type: "POST",
    url: "/submit_items",
    data: opt,
    cache: false,
    success: function(resp) {
      if (resp.result) {
        if (resp.result == "success") {
          window.location.href = resp.url;
        }
      } else {
        $("#err_msg")
          .text(resp.msg)
          .show();
      }
    },
    error: function(resp) {
      $("#err_msg")
        .text(JSON.stringify(resp))
        .show()
        .fadeOut(10000);
    }
  });
}
