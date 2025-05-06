document.addEventListener('DOMContentLoaded', function () {
    const roleSelect = document.getElementById('role');
    const disabledFields = document.getElementById('disabled-fields');
    const writerFields = document.getElementById('writer-fields');

    roleSelect.addEventListener('change', function () {
        const selectedRole = this.value;

        disabledFields.style.display = 'none';
        writerFields.style.display = 'none';

        if (selectedRole === 'disabled') {
            disabledFields.style.display = 'block';
        } else if (selectedRole === 'writer') {
            writerFields.style.display = 'block';
        }
    });
});
