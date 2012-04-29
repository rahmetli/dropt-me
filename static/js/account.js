$(document).ready(function(){
	// initial loading
	$('#directory').load("/handle_directory_change/", {path : "/Public/"}, add_handler_directory);

	function add_handler_directory()
	{
		$('#directory ul li a').click(_click_handler_directory);
		$('.loading').hide('slow');
		$('#directory').show('slow');
	}
	function _click_handler_directory(e){
		var path = $(this).text();
		var parent = $(this).parent('li');
		var current = $('#current_path span').text();
		if(parent.hasClass('folder'))
		{
			var new_path = current+path+"/";
		}
		else if(parent.hasClass('up') && current != "/Public/")
		{
			var splitted = current.split('/')
			var i;
			var new_path='/';
			for(i=1;i<splitted.length-2;i++)
			{
				new_path += splitted[i] + "/" ;
			}
		}
		else
		{
			return false;
		}
		$('#directory').hide('fast');
		$('.loading').show('slow');
		$.ajax({
			url : "/handle_directory_change/",
			data : {path : new_path},
			dataType : "text",
			type : "POST",
			contentType : "text/html",
			success : function(data){
				$('#directory').html(data);	
			}
		}).done(add_handler_directory);
	}
})

