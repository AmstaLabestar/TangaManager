document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-animate-card]').forEach((card, index) => {
    window.setTimeout(() => card.classList.add('is-revealed'), index * 80);
  });

  const filterButtons = document.querySelectorAll('[data-filter]');
  const rows = document.querySelectorAll('[data-smart-list] .install-row');

  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const filter = button.dataset.filter;

      filterButtons.forEach((item) => item.classList.remove('is-selected'));
      button.classList.add('is-selected');

      rows.forEach((row) => {
        const hasProblem = Number(row.dataset.problemCount || 0) > 0;
        const shouldShow =
          filter === 'all' ||
          row.dataset.status === filter ||
          (filter === 'probleme' && hasProblem);

        row.classList.toggle('is-hidden', !shouldShow);
      });
    });
  });
});
