document.addEventListener('DOMContentLoaded', () => {
  const postDetailModalEl = document.getElementById('postDetailModal');
  const postDetailContent = document.getElementById('postDetailContent');
  const detailModal = new bootstrap.Modal(postDetailModalEl);

  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  // 投稿カードクリック時のモーダル表示処理
  function bindPostDetailTriggers() {
    document.querySelectorAll('.post-detail-trigger').forEach(el => {
      el.addEventListener('click', async (e) => {
        e.preventDefault();
        const postId = el.dataset.postId;
        try {
          const res = await fetch(`/posts/${postId}/detail/ajax/`);
          const data = await res.json();
          postDetailContent.innerHTML = data.html;
          detailModal.show();

          // モーダル内のいいねボタン再バインド
          bindLikeButtons();
        } catch (err) {
          console.error('投稿詳細取得エラー:', err);
        }
      });
    });
  }

  // 一覧 + モーダル共通 いいねボタン処理
  function bindLikeButtons() {
    document.querySelectorAll('.btn-like').forEach(button => {
      // 重複バインド防止のため、一旦イベント解除
      button.removeEventListener('click', handleLikeClick);
      button.addEventListener('click', handleLikeClick);
    });
  }

  // いいねボタン押下時の共通処理
  async function handleLikeClick(e) {
    e.preventDefault();
    const button = e.currentTarget;
    const postId = button.dataset.postId;

    try {
      const res = await fetch(`/posts/${postId}/like/ajax/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      });
      const data = await res.json();

      // 一覧 + モーダル両方更新
      updateLikeDisplay(postId, data.liked, data.like_count);

    } catch (err) {
      console.error('いいね処理エラー:', err);
    }
  }

  // いいね表示更新（一覧＆モーダル両方）
  function updateLikeDisplay(postId, liked, likeCount) {
    document.querySelectorAll(`.btn-like[data-post-id="${postId}"]`).forEach(button => {
      const icon = button.querySelector('i');
      const likeCountSpan = button.nextElementSibling;
      icon.className = liked ? 'fas fa-check' : 'fas fa-thumbs-up';
      likeCountSpan.textContent = likeCount;
    });
  }

  // 初期バインド
  bindPostDetailTriggers();
  bindLikeButtons();
});
