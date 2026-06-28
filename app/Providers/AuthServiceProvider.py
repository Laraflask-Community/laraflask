"""
Auth Service Provider
Define authorization gates and policies.
"""

from laraflask.core.providers import ServiceProvider


class AuthServiceProvider(ServiceProvider):
    """
    Register authentication / authorization services.
    """

    # Map model class paths → policy class paths
    policies = {
        # 'app.Models.Post.Post': 'app.Policies.PostPolicy.PostPolicy',
    }

    def register(self):
        pass

    def boot(self):
        """Register policies and gate abilities."""
        from laraflask.auth.auth import Gate

        # Register model policies
        for model_path, policy_path in self.policies.items():
            try:
                import importlib
                m_mod, m_cls = model_path.rsplit('.', 1)
                p_mod, p_cls = policy_path.rsplit('.', 1)
                model  = getattr(importlib.import_module(m_mod), m_cls)
                policy = getattr(importlib.import_module(p_mod), p_cls)
                Gate.policy(model, policy)
            except ImportError:
                pass

        # Register gate abilities
        # Gate.define('update-post', lambda user, post: post.user_id == user.id)
        # Gate.define('admin', lambda user: user.role == 'admin')
