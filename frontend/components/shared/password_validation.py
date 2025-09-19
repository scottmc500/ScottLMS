"""
Password validation utilities and UI components
"""

import re
import streamlit as st


def validate_password(password, username=None, first_name=None, last_name=None, email=None):
    """
    Comprehensive password validation
    Returns (is_valid, error_messages)
    """
    errors = []
    
    # Basic length check
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password must be no more than 128 characters long")
    
    # Character type requirements
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        errors.append("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
    
    # Common password check
    common_passwords = [
        'password', 'password123', '123456', '12345678', 'qwerty', 'abc123',
        'admin', 'letmein', 'welcome', 'monkey', '1234567890', 'password1',
        'iloveyou', 'princess', 'rockyou', '123456789', '12345', 'football'
    ]
    
    if password.lower() in common_passwords:
        errors.append("Password is too common. Please choose a more unique password")
    
    # Sequential characters check
    if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
        errors.append("Password should not contain sequential characters (123, abc, etc.)")
    
    # Repeated characters check
    if re.search(r'(.)\1{2,}', password):
        errors.append("Password should not contain 3 or more repeated characters")
    
    # Personal information check
    if username and len(username) > 2 and username.lower() in password.lower():
        errors.append("Password should not contain your username")
    
    if first_name and len(first_name) > 2 and first_name.lower() in password.lower():
        errors.append("Password should not contain your first name")
    
    if last_name and len(last_name) > 2 and last_name.lower() in password.lower():
        errors.append("Password should not contain your last name")
    
    if email:
        email_parts = email.split('@')[0].lower()
        if len(email_parts) > 2 and email_parts in password.lower():
            errors.append("Password should not contain your email address")
    
    return len(errors) == 0, errors


def get_password_strength_score(password):
    """Calculate password strength score (0-100)"""
    score = 0
    
    # Length scoring
    if len(password) >= 8:
        score += 25
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10
    
    # Character type scoring
    if re.search(r'[a-z]', password):
        score += 10
    if re.search(r'[A-Z]', password):
        score += 10
    if re.search(r'\d', password):
        score += 15
    if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        score += 20
    
    # Complexity bonus
    unique_chars = len(set(password))
    if unique_chars > len(password) * 0.7:
        score += 10
    
    return min(score, 100)


def display_inline_password_requirements(password, username=None, first_name=None, last_name=None, email=None):
    """Display compact inline password requirements indicator"""
    if not password:
        return
    
    # Check each requirement
    checks = {
        'length': len(password) >= 8,
        'upper': bool(re.search(r'[A-Z]', password)),
        'lower': bool(re.search(r'[a-z]', password)),
        'digit': bool(re.search(r'\d', password)),
        'special': bool(re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password)),
        'common': password.lower() not in ['password', 'password123', '123456', '12345678', 'qwerty', 'abc123', 'admin', 'letmein', 'welcome', 'monkey', '1234567890', 'password1'],
        'sequential': not bool(re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower())),
        'repeated': not bool(re.search(r'(.)\1{2,}', password))
    }
    
    # Personal info checks
    if username and len(username) > 2:
        checks['username'] = username.lower() not in password.lower()
    
    # Create compact indicator
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Requirements indicators in a compact format
        requirements = [
            ("8+ chars", checks['length']),
            ("A-Z", checks['upper']),
            ("a-z", checks['lower']),
            ("0-9", checks['digit']),
            ("!@#", checks['special']),
            ("No common", checks['common']),
            ("No sequence", checks['sequential']),
            ("No repeat", checks['repeated'])
        ]
        
        if 'username' in checks:
            requirements.append(("No username", checks['username']))
        
        # Create inline indicators
        indicators = []
        for label, passed in requirements:
            if passed:
                indicators.append(f"✅ {label}")
            else:
                indicators.append(f"❌ {label}")
        
        # Display in rows of 4
        for i in range(0, len(indicators), 4):
            row_indicators = indicators[i:i+4]
            st.markdown(" • ".join(row_indicators))
    
    with col2:
        # Strength meter
        score = get_password_strength_score(password)
        if score < 30:
            st.error(f"Weak ({score})")
        elif score < 60:
            st.warning(f"Fair ({score})")
        elif score < 80:
            st.info(f"Good ({score})")
        else:
            st.success(f"Strong ({score})")


def display_password_requirements_checklist(password, username=None, first_name=None, last_name=None, email=None):
    """Display detailed password requirements checklist with real-time validation"""
    if not password:
        st.info("👆 Enter a password above to see requirements checklist")
        return
    
    st.markdown("### 📋 Password Requirements Checklist")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📏 Length Requirements:**")
        
        # Length checks
        if len(password) >= 8:
            st.success("✅ At least 8 characters")
        else:
            st.error(f"❌ At least 8 characters (current: {len(password)})")
            
        if len(password) <= 128:
            st.success("✅ No more than 128 characters")
        else:
            st.error(f"❌ No more than 128 characters (current: {len(password)})")
        
        st.markdown("**🔤 Character Types:**")
        
        # Character type checks
        if re.search(r'[a-z]', password):
            st.success("✅ Lowercase letters (a-z)")
        else:
            st.error("❌ Lowercase letters (a-z)")
            
        if re.search(r'[A-Z]', password):
            st.success("✅ Uppercase letters (A-Z)")
        else:
            st.error("❌ Uppercase letters (A-Z)")
            
        if re.search(r'\d', password):
            st.success("✅ Numbers (0-9)")
        else:
            st.error("❌ Numbers (0-9)")
            
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            st.success("✅ Special characters (!@#$%...)")
        else:
            st.error("❌ Special characters (!@#$%...)")
    
    with col2:
        st.markdown("**🛡️ Security Checks:**")
        
        # Common password check
        common_passwords = [
            'password', 'password123', '123456', '12345678', 'qwerty', 'abc123',
            'admin', 'letmein', 'welcome', 'monkey', '1234567890', 'password1',
            'iloveyou', 'princess', 'rockyou', '123456789', '12345', 'football'
        ]
        
        if password.lower() not in common_passwords:
            st.success("✅ Not a common password")
        else:
            st.error("❌ Not a common password")
        
        # Sequential characters check
        if not re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            st.success("✅ No sequential characters")
        else:
            st.error("❌ No sequential characters (123, abc)")
        
        # Repeated characters check
        if not re.search(r'(.)\1{2,}', password):
            st.success("✅ No repeated characters")
        else:
            st.error("❌ No 3+ repeated characters (aaa)")
        
        st.markdown("**👤 Personal Info Checks:**")
        
        # Personal information checks
        personal_info_clean = True
        
        if username and len(username) > 2 and username.lower() in password.lower():
            st.error("❌ Doesn't contain username")
            personal_info_clean = False
        elif username:
            st.success("✅ Doesn't contain username")
        
        if first_name and len(first_name) > 2 and first_name.lower() in password.lower():
            st.error("❌ Doesn't contain first name")
            personal_info_clean = False
        elif first_name:
            st.success("✅ Doesn't contain first name")
        
        if last_name and len(last_name) > 2 and last_name.lower() in password.lower():
            st.error("❌ Doesn't contain last name")
            personal_info_clean = False
        elif last_name:
            st.success("✅ Doesn't contain last name")
        
        if email:
            email_parts = email.split('@')[0].lower()
            if len(email_parts) > 2 and email_parts in password.lower():
                st.error("❌ Doesn't contain email")
                personal_info_clean = False
            else:
                st.success("✅ Doesn't contain email")
        
        if not any([username, first_name, last_name, email]) or personal_info_clean:
            if not any([username, first_name, last_name, email]):
                st.info("ℹ️ Personal info checks pending")
    
    # Overall score and progress bar
    score = get_password_strength_score(password)
    st.markdown("### 📊 Password Strength Score")
    
    # Create a progress bar
    progress = score / 100
    if score < 30:
        st.error(f"🔴 **Weak Password** - Score: {score}/100")
        st.progress(progress)
        st.markdown("🚨 **This password is not secure enough. Please improve it.**")
    elif score < 60:
        st.warning(f"🟡 **Moderate Password** - Score: {score}/100")
        st.progress(progress)
        st.markdown("⚠️ **This password could be stronger. Consider adding more complexity.**")
    elif score < 80:
        st.info(f"🔵 **Strong Password** - Score: {score}/100")
        st.progress(progress)
        st.markdown("👍 **Good password! You're on the right track.**")
    else:
        st.success(f"🟢 **Very Strong Password** - Score: {score}/100")
        st.progress(progress)
        st.markdown("🎉 **Excellent! This is a very secure password.**")


def display_password_strength(password):
    """Display simple password strength meter (legacy function for backwards compatibility)"""
    if not password:
        return
        
    score = get_password_strength_score(password)
    
    if score < 30:
        st.error(f"🔴 Weak Password (Score: {score}/100)")
    elif score < 60:
        st.warning(f"🟡 Moderate Password (Score: {score}/100)")
    elif score < 80:
        st.info(f"🟢 Strong Password (Score: {score}/100)")
    else:
        st.success(f"🟢 Very Strong Password (Score: {score}/100)")
