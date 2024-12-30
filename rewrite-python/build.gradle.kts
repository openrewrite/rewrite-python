plugins {
    id("org.openrewrite.build.language-library")
}

val latest = if (project.hasProperty("releasing")) "latest.release" else "latest.integration"

tasks.compileJava {
    options.release = 8
}

dependencies {
    compileOnly("org.openrewrite:rewrite-test")
    implementation("org.openrewrite:rewrite-remote-java:$latest") {
        exclude(group = "org.openrewrite", module = "rewrite-python")
    }

    implementation(platform("org.openrewrite:rewrite-bom:$latest"))
    implementation("org.openrewrite:rewrite-core")
    implementation("org.openrewrite:rewrite-java")
    // FIXME: temporary until we've decided how to best integrate into CLI
    runtimeOnly(project(":rewrite-python-remote"))

    testImplementation("org.openrewrite:rewrite-test")
    testImplementation("org.junit-pioneer:junit-pioneer:latest.release")
}

val pythonProjectDir = file("../rewrite")
val outputDir = layout.buildDirectory.dir("resources/main/META-INF")
val requirementsFile = outputDir.map { it.file("python-requirements.txt") }

tasks.test {
    maxParallelForks = 1
    environment("PATH", "${pythonProjectDir.resolve(".venv/bin").absolutePath}${File.pathSeparator}${System.getenv("PATH")}")
}

tasks.register("prepareOutputDir") {
    doLast {
        outputDir.get().asFile.mkdirs()
    }
}

tasks.register<Exec>("exportPythonRequirements") {
    dependsOn("prepareOutputDir")
    workingDir = pythonProjectDir
    commandLine("sh", "-c", "uv export --no-header --frozen --no-hashes --no-emit-project --no-dev --no-emit-package openrewrite-remote -o ${requirementsFile.get().asFile.absolutePath}")
    standardOutput = System.out
    errorOutput = System.err
}

tasks.register("appendOpenRewriteRequirements") {
    dependsOn("exportPythonRequirements")
    doLast {
        val file = requirementsFile.get().asFile
        file.appendText("openrewrite${generatePipVersionConstraint(project.version.toString(), false)}\n")
        file.appendText("openrewrite-remote${generatePipVersionConstraint(getDirectDependencyVersion("org.openrewrite:rewrite-remote-java"), true)}\n")
    }
}

tasks.named("processResources") {
    dependsOn("appendOpenRewriteRequirements")
}

fun generatePipVersionConstraint(version: String, boundByMajorVersion: Boolean): String {
    if (version.endsWith("-SNAPSHOT")) {
        return "<${version.replace("-SNAPSHOT", "")}"
    }
    val versionParts = version.split(".")
    if (versionParts.size != 3) {
        throw IllegalArgumentException("Invalid version format: $version")
    }

    val major = versionParts[0].toInt()
    val minor = versionParts[1].toInt()
    val patch = versionParts[2]

    return if (boundByMajorVersion) {
        val nextMajor = (major + 1).toString() + ".0.0"
        ">=${major}.${minor}.${patch},<${nextMajor}"
    } else {
        val nextMinor = major.toString() + "." + (minor + 1) + ".0"
        ">=${major}.${minor}.${patch},<${nextMinor}"
    }
}

fun Task.getDirectDependencyVersion(dependencyName: String): String {
    val compileClasspathConfig = project.configurations.getByName("compileClasspath")
    var version = ""
    compileClasspathConfig.resolvedConfiguration.firstLevelModuleDependencies.forEach { dependency ->
        if ((dependency.module.id.group + ':' + dependency.module.id.name) == dependencyName) {
            version = dependency.module.id.version
        }
    }
    return version
}
