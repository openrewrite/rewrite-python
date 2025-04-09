pluginManagement {
    repositories {
        mavenLocal()
        gradlePluginPortal()
    }
}

rootProject.name = "rewrite-python"

plugins {
    id("com.gradle.develocity") version "3.+"
    id("com.gradle.common-custom-user-data-gradle-plugin") version "1.12.1"
}

include("rewrite-python")
include("rewrite-python-remote")
include("rewrite-test-engine-remote")

develocity {
    server = "https://ge.openrewrite.org/"

    val isCiServer = System.getenv("CI")?.equals("true") ?: false
    val accessKey = System.getenv("GRADLE_ENTERPRISE_ACCESS_KEY")
    val authenticated = !accessKey.isNullOrBlank()
    buildCache {
        remote(develocity.buildCache) {
            isEnabled = true
            isPush = isCiServer && authenticated
        }
    }

    buildScan {
        capture {
            fileFingerprints = true
        }

        publishing {
            onlyIf {
                authenticated
            }
        }

        uploadInBackground = !isCiServer
    }
}
