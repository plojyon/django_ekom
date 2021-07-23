function refresh_filters() {
	submissions.forEach((submission, i) => {
		var filter_letnik = document.getElementById("letnik_select").value;
		var filter_type = document.getElementById("type_select").value;
		var filter_predmet = document.getElementById("predmet_select").value;
		var filter_professor = document.getElementById("professor_select").value;
		var submission_letnik = submission ["year"];
		var submission_type = submission ["type_name"];
		var submission_predmet = submission ["subject_slug"];
		var submission_professor = submission ["prof_name"];
		var elementname = document.getElementById(submission ["filename"]);
		if ((filter_letnik == submission_letnik || filter_letnik == "" || submission_letnik == "0") &&
			(filter_type == submission_type || filter_type == "") &&
			(filter_predmet == submission_predmet || filter_predmet == "") &&
			(filter_professor == submission_professor || filter_professor == "")) {
			elementname.classList.remove("hidden");
		} else {
			elementname.classList.add("hidden");
		}
	});
	noresult.classList.add("hidden");
	var count_hidden = document.querySelectorAll(".hidden").length;
	var count_all = document.getElementById("submissions_list").childElementCount-1;
	if (count_all == count_hidden) {
		noresult.classList.remove("hidden");
	} else {
		noresult.classList.add("hidden");
	}
}
