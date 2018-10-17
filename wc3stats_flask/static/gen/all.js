function thisIsAFunction(){
    return "my string";
}
$(document).ready(function() {

    function convertDataTables(){
        var datatables = $(".datatable");

        for(var i=0;i<datatables.length;i++){
            if(!$.fn.dataTable.isDataTable("#" + datatables[i].id)){
                $("#" + datatables[i].id).DataTable({
                    paging: false,
                    info: false,
                    searching: false,
                    order: [],
                    responsive: true
                    })
            }
        }

        datatables = $(".datatablePaging");

        for(var i=0;i<datatables.length;i++){
            if(!$.fn.dataTable.isDataTable("#" + datatables[i].id)){
                $("#" + datatables[i].id).DataTable({
                    paging: true,
                    info: false,
                    searching: true,
                    order: [],
                    responsive: true
                })
            }
        }
    }

	$('#inputName').on('input', function(event){
		var playerName = $('#inputName').val();
		var inputReplays = document.getElementById("inputReplays");
		if(playerName.length > 0 && inputReplays.files.length > 0){
			$('#btnSubmit').removeAttr("disabled");
		}else{
			$('#btnSubmit').attr("disabled", "true");
		}
	});
	$('#inputReplays').on('submit', function(event){
		event.preventDefault();
	});
	$('#inputReplays').on('change', function(event){
		event.preventDefault();
		var playerName = $('#inputName').val();
		if(this.files.length > 0 && playerName.length > 0){
			$('#btnSubmit').removeAttr("disabled");
		}else{
			$('#btnSubmit').attr("disabled", "true");
		}
	});

	$('form').on('submit', function(event) {
		event.preventDefault();
		$('#progressBar').attr('aria-valuenow', 0).css('width', 0 + '%').text(0 + '%');

		var formData = new FormData($('form')[0]);

		var inputReplays = document.getElementById("inputReplays");
		var replays = inputReplays.files;

		formData.set("playerName", $('#inputName').val());

		var dates = {};

		for(var r = 0; r < replays.length; r++){
			dates[replays[r].name] = replays[r].lastModified;
		}

		formData.set("dates", JSON.stringify(dates));		
		$.ajax({
			xhr : function() {
				var xhr = new window.XMLHttpRequest();
				xhr.upload.addEventListener('progress', function(e) {
					if (e.lengthComputable) {

						console.log('Bytes Loaded: ' + e.loaded);
						console.log('Total Size: ' + e.total);
						console.log('Percentage Uploaded: ' + (e.loaded / e.total))

						var percent = Math.round((e.loaded / e.total) * 100);

						$('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
					}
				});
				return xhr;
			},
			type : 'POST',
			url : '/upload',
			data : formData,
			processData : false,
			contentType : false,
			success : function(response) {
				$("#bodyContainer").html(response);
				convertDataTables();
			}
		});
	});
});