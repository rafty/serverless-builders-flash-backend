AWS.config.region = CognitoConfig.region;
AWSCognito.config.region = CognitoConfig.region;

const TargetUserPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool({ 
    UserPoolId: CognitoConfig.userPoolId,
    ClientId: CognitoConfig.appClientId
});

const SignInStatus = {
    currentCognitoUser: TargetUserPool.getCurrentUser(),
    lastIdentityToken: null,
    lastAccessToken: null
};

(() => {
    // Cognito User Pool: Check sign-in status and get user session.
    const currentPage = location.pathname.substr(location.pathname.lastIndexOf('/') + 1);

    if (!SignInStatus.currentCognitoUser) {
        console.log("Cognito User Pool: Not signed in.");
        console.log("Cognito User Pool: Sign-in status:", SignInStatus);
        if (currentPage == 'mypage.html') {
            // alert('Move to login page!');
            $(location).attr('href', 'login.html');
        }
    } else {
        SignInStatus.currentCognitoUser.getSession((err, session) => {
            if (err) {
                console.error(err);
                SignInStatus.currentCognitoUser.clearCachedTokens();
                SignInStatus.lastIdentityToken = null;
                SignInStatus.lastAccessToken = null;
                SignInStatus.currentCognitoUser = null;
                console.log("Cognito User Pool: Error at getting session.");
                console.log("Cognito User Pool: Sign-in status:", SignInStatus);
                if (currentPage == 'mypage.html') {
                    // alert('Move to login page!');
                    $(location).attr('href', 'login.html');
                }
            } else {
                SignInStatus.lastIdentityToken = session.getIdToken().getJwtToken();
                SignInStatus.lastAccessToken = session.getAccessToken().getJwtToken();
                console.log("Cognito User Pool: Signed in.");
                console.log("Cognito User Pool: Sign-in status:", SignInStatus);
                if (currentPage == 'login.html') {
                    // alert('Move to MyPage!');
                    $(location).attr('href', 'mypage.html');
                }
            }
        });
    }

    // Cognito Identity Pool: Get AWS credentials.
    const logins = {};
    const providerName = "cognito-idp." + CognitoConfig.region + ".amazonaws.com/" + CognitoConfig.userPoolId;
    logins[providerName] = SignInStatus.lastIdentityToken;

    AWS.config.credentials = new AWS.CognitoIdentityCredentials({
        IdentityPoolId: CognitoConfig.identityPoolId,
        Logins: logins
    });

    AWS.config.credentials.get((err) => {
        if (err) {
            console.error(err);
        } else {
            console.log("Cognito Identity Pool: AWS credentials:", AWS.config.credentials);

            const sts = new AWS.STS();
            const params = {};
            sts.getCallerIdentity(params, function(err, data) {
                if (err) {
                    console.log("Cognito Identity Pool: IAM Role information:", err);
                } else {
                    console.log("Cognito Identity Pool: IAM Role information:", data);
                    $('#iam-role').val(
                        '{\n' +
                        '  Account: ' + data.Account + '\n' + 
                        '  UserId: ' + data.UserId + '\n' + 
                        '  Arn: ' + data.Arn +'\n' +
                        '}'
                    );
                }
            });
        }
    });
})();

const signUp = (username, password, email, callback) => {
    const attributeList = [];
    attributeList.push(
        new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute({
            Name: 'email',
            Value: email
        })
    );

    TargetUserPool.signUp(username, password, attributeList, null, (err, result) => {
        if (err) {
            alert(err);
            callback(err, result);
            return;
        }
        const cognitoUser = result.user;
        const signUpResult = {
            username: cognitoUser.getUsername()
        };
        console.log("Sign-up result:", signUpResult);
        callback(err, signUpResult);
    });
};

const activate = (username, confirmationcode, callback) => {
    const cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser({
        Username: username,
        Pool: TargetUserPool
    });

    cognitoUser.confirmRegistration(confirmationcode, true, (err, result) => {
        if (err) {
            alert(err);
            callback(err, result);
            return;
        }
        console.log("Activation result:", result);
        callback(err, result);
    });
};

const signIn = (username, password, callbacks) => {
    const cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser({
        Username: username,
        Pool: TargetUserPool
    });

    const authenticationDetails = new AWSCognito.CognitoIdentityServiceProvider.AuthenticationDetails({
        Username: username,
        Password: password
    });

    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: (result) => {
            console.log("Sign-in result:", result);
            callbacks.onSuccess(result);
        },
        onFailure: (err) => {
            alert(err);
            callbacks.onFailure(err);
        }
    });
}

const signOut = (callback) => {
    SignInStatus.currentCognitoUser.signOut();
    if (AWS.config.credentials) {
        AWS.config.credentials.clearCachedId();
    }
    callback(null, null);
};
