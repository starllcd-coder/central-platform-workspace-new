(function () {
  const menuButton = document.querySelector('[data-menu-btn]');
  const sidebar = document.querySelector('.sidebar');
  if (menuButton && sidebar) {
    menuButton.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
  }

  const tenantSearch = document.querySelector('[data-tenant-search]');
  if (tenantSearch) {
    tenantSearch.addEventListener('input', function (e) {
      const q = e.target.value.trim().toLowerCase();
      document.querySelectorAll('[data-tenant-row]').forEach(function (row) {
        row.style.display = row.innerText.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }
})();
