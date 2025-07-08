// smooth scroll to prediction
document
  .querySelector('.btn-primary')
  .addEventListener('click', (e) => {
    e.preventDefault();
    document
      .querySelector('#prediction')
      .scrollIntoView({ behavior: 'smooth' });
  });

// form handling
document
  .getElementById('predictForm')
  .addEventListener('submit', function (e) {
    e.preventDefault();
    const fields = [
      'age','gender','race','admissionType','dischargeDisposition',
      'admissionSource','timeInHospital','numLabProcedures',
      'numProcedures','numMedications','numOutpatient',
      'numEmergency','numInpatient','numDiagnoses',
      'maxGlucoseSerum','a1cResult','change','diabetesMed'
    ];
    const data = {};
    fields.forEach((f) => {
      data[f] = document.getElementById(f).value;
    });
    console.log('Submitting prediction payload:', data);
    // TODO: hook up to your backend prediction API
    alert('Prediction submitted!\nCheck console for payload.');
  });
